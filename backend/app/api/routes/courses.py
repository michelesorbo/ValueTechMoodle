import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUserDep, SessionDep
from app.models import Course, ScormPackage
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate
from app.schemas.scorm import ScormPackageRead

router = APIRouter(prefix="/courses", tags=["courses"])


async def _get_course_or_404(session: SessionDep, course_id: uuid.UUID) -> Course:
    course = await session.get(Course, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corso non trovato")
    return course


@router.get("", response_model=list[CourseRead])
async def list_courses(session: SessionDep, _user: CurrentUserDep) -> list[Course]:
    result = await session.scalars(select(Course).order_by(Course.created_at.desc()))
    return list(result)


@router.post("", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate, session: SessionDep, _user: CurrentUserDep
) -> Course:
    course = Course(**payload.model_dump())
    session.add(course)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Codice corso già esistente") from exc
    await session.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: uuid.UUID, session: SessionDep, _user: CurrentUserDep) -> Course:
    return await _get_course_or_404(session, course_id)


@router.patch("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: uuid.UUID, payload: CourseUpdate, session: SessionDep, _user: CurrentUserDep
) -> Course:
    course = await _get_course_or_404(session, course_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    await session.commit()
    await session.refresh(course)
    return course


@router.get("/{course_id}/packages", response_model=list[ScormPackageRead])
async def list_course_packages(
    course_id: uuid.UUID, session: SessionDep, _user: CurrentUserDep
) -> list[ScormPackage]:
    await _get_course_or_404(session, course_id)
    result = await session.scalars(
        select(ScormPackage)
        .where(ScormPackage.course_id == course_id)
        .order_by(ScormPackage.created_at)
    )
    return list(result)
