from functools import lru_cache
from pathlib import Path

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione applicativa letta da variabili d'ambiente / file .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ValueTech LMS"
    environment: str = Field(default="development", pattern="^(development|test|production)$")

    # postgresql+psycopg://user:pass@host:5432/db  (driver psycopg 3, async-capable)
    database_url: PostgresDsn = PostgresDsn("postgresql+psycopg://lms:lms@localhost:5432/lms")
    db_echo: bool = False

    cors_origins: list[str] = ["http://localhost:5173"]

    # Dove vengono estratti i pacchetti SCORM caricati
    scorm_storage_dir: Path = Path("./storage/scorm")
    scorm_max_upload_mb: int = 500

    # TODO(corso): sostituire con autenticazione reale (vedi docs/specifiche.md §RF-01)
    demo_user_email: str = "demo@valuetech.local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
