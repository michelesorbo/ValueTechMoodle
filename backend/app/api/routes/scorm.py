import uuid
from typing import Annotated, Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select

from app.api.deps import CurrentUserDep, SessionDep, SettingsDep
from app.models import Course, ScormAttempt, ScormPackage, ScormVersion
from app.schemas.scorm import (
    ScormAttemptRead,
    ScormCommit,
    ScormLaunch,
    ScormPackageRead,
)
from app.services.scorm.storage import PackageError, extract_package, remove_package

router = APIRouter(prefix="/scorm", tags=["scorm"])

SCORM_CONTENT_PREFIX = "/scorm-content"


@router.post("/packages", response_model=ScormPackageRead, status_code=status.HTTP_201_CREATED)
async def upload_package(
    session: SessionDep,
    settings: SettingsDep,
    _user: CurrentUserDep,
    course_id: Annotated[uuid.UUID, Form()],
    file: Annotated[UploadFile, File(description="Pacchetto SCORM (.zip)")],
) -> ScormPackage:
    if await session.get(Course, course_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corso non trovato")

    if file.size is not None and file.size > settings.scorm_max_upload_mb * 1024 * 1024:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Pacchetto troppo grande")

    settings.scorm_storage_dir.mkdir(parents=True, exist_ok=True)
    try:
        # zipfile è sincrono e CPU/IO bound: lo spostiamo fuori dall'event loop
        package_id, manifest = await run_in_threadpool(
            extract_package, file.file, settings.scorm_storage_dir
        )
    except PackageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc

    package = ScormPackage(
        id=package_id,
        course_id=course_id,
        title=manifest.title,
        version=manifest.version,
        launch_path=manifest.launch_path,
        manifest=manifest.to_json(),
    )
    session.add(package)
    try:
        await session.commit()
    except Exception:
        remove_package(settings.scorm_storage_dir, package_id)
        raise
    await session.refresh(package)
    return package


@router.get("/packages/{package_id}/launch", response_model=ScormLaunch)
async def launch_package(
    package_id: uuid.UUID, session: SessionDep, user: CurrentUserDep
) -> ScormLaunch:
    package = await session.get(ScormPackage, package_id)
    if package is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pacchetto non trovato")

    attempt = await session.scalar(
        select(ScormAttempt).where(
            ScormAttempt.package_id == package_id, ScormAttempt.user_id == user.id
        )
    )
    if attempt is None:
        attempt = ScormAttempt(package_id=package_id, user_id=user.id, cmi={})
        session.add(attempt)
        await session.commit()
        await session.refresh(attempt)

    return ScormLaunch(
        package_id=package.id,
        attempt_id=attempt.id,
        version=package.version,
        launch_url=f"{SCORM_CONTENT_PREFIX}/{package.id}/{package.launch_path}",
        commit_url=f"/api/scorm/attempts/{attempt.id}/commit",
        cmi=attempt.cmi,
        learner_id=str(user.id),
        learner_name=user.full_name,
    )


def _dig(data: dict[str, Any], *path: str) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _to_float(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


@router.post("/attempts/{attempt_id}/commit")
async def commit_attempt(
    attempt_id: uuid.UUID, payload: ScormCommit, session: SessionDep, user: CurrentUserDep
) -> dict[str, Any]:
    """Endpoint chiamato da scorm-again (``lmsCommitUrl``) su Commit/Terminate.

    La risposta rispetta il formato atteso dal responseHandler di default di
    scorm-again: ``{"result": true, "errorCode": 0}``.
    """
    attempt = await session.get(ScormAttempt, attempt_id)
    if attempt is None or attempt.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tentativo non trovato")

    package = await session.get(ScormPackage, attempt.package_id)
    assert package is not None
    cmi = payload.cmi

    if package.version is ScormVersion.SCORM_12:
        lesson_status = _dig(cmi, "core", "lesson_status")
        attempt.completion_status = lesson_status
        attempt.success_status = lesson_status if lesson_status in ("passed", "failed") else None
        attempt.score_raw = _to_float(_dig(cmi, "core", "score", "raw"))
        attempt.total_time = _dig(cmi, "core", "total_time") or attempt.total_time
    else:
        attempt.completion_status = _dig(cmi, "completion_status")
        attempt.success_status = _dig(cmi, "success_status")
        attempt.score_raw = _to_float(_dig(cmi, "score", "raw"))
        attempt.total_time = _dig(cmi, "total_time") or attempt.total_time

    attempt.cmi = cmi
    await session.commit()
    return {"result": True, "errorCode": 0}


@router.get("/attempts/{attempt_id}", response_model=ScormAttemptRead)
async def get_attempt(
    attempt_id: uuid.UUID, session: SessionDep, user: CurrentUserDep
) -> ScormAttempt:
    attempt = await session.get(ScormAttempt, attempt_id)
    if attempt is None or attempt.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tentativo non trovato")
    return attempt
