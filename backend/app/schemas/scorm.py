import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.scorm import ScormVersion


class ScormPackageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    version: ScormVersion
    launch_path: str
    created_at: datetime


class ScormLaunch(BaseModel):
    """Tutto ciò che serve al player per inizializzare scorm-again e l'iframe."""

    package_id: uuid.UUID
    attempt_id: uuid.UUID
    version: ScormVersion
    launch_url: str
    commit_url: str
    cmi: dict[str, Any]
    learner_id: str
    learner_name: str


class ScormCommit(BaseModel):
    """Payload inviato da scorm-again (lmsCommitUrl) a ogni Commit/Finish."""

    model_config = ConfigDict(extra="allow")

    cmi: dict[str, Any]


class ScormAttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    package_id: uuid.UUID
    user_id: uuid.UUID
    completion_status: str | None
    success_status: str | None
    score_raw: float | None
    total_time: str | None
    updated_at: datetime
