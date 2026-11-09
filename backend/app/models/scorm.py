from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class ScormVersion(enum.StrEnum):
    SCORM_12 = "1.2"
    SCORM_2004 = "2004"


class ScormPackage(UUIDPkMixin, TimestampMixin, Base):
    """Pacchetto SCORM caricato ed estratto su storage."""

    __tablename__ = "scorm_packages"

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    version: Mapped[ScormVersion] = mapped_column(
        Enum(ScormVersion, name="scorm_version", values_callable=lambda e: [m.value for m in e])
    )
    # Path relativo (dentro la cartella del pacchetto) della risorsa SCO da lanciare
    launch_path: Mapped[str] = mapped_column(String(1024))
    # Manifest normalizzato (organizzazioni, item, risorse) per usi futuri (multi-SCO)
    manifest: Mapped[dict[str, Any]] = mapped_column(JSONB)

    course: Mapped[Course] = relationship(back_populates="packages")
    attempts: Mapped[list[ScormAttempt]] = relationship(
        back_populates="package", cascade="all, delete-orphan"
    )


class ScormAttempt(UUIDPkMixin, TimestampMixin, Base):
    """Tentativo di fruizione: contiene il CMI data model serializzato da scorm-again."""

    __tablename__ = "scorm_attempts"
    __table_args__ = (UniqueConstraint("package_id", "user_id", name="uq_attempt_package_user"),)

    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("scorm_packages.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # Campi denormalizzati dal CMI per reportistica rapida (indicizzabili)
    completion_status: Mapped[str | None] = mapped_column(String(32))
    success_status: Mapped[str | None] = mapped_column(String(32))
    score_raw: Mapped[float | None]
    total_time: Mapped[str | None] = mapped_column(String(64))

    cmi: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")

    package: Mapped[ScormPackage] = relationship(back_populates="attempts")
    user: Mapped[User] = relationship()
