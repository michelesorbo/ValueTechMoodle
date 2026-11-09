import os
import tempfile
from collections.abc import AsyncIterator

# Le variabili vanno impostate PRIMA di importare l'app (Settings è in cache)
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://lms:lms@localhost:5432/lms_test")
os.environ["ENVIRONMENT"] = "test"
os.environ["SCORM_STORAGE_DIR"] = tempfile.mkdtemp(prefix="scorm-test-")

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.db import engine
from app.main import app
from app.models import Base


@pytest.fixture(scope="session")
async def _schema() -> AsyncIterator[None]:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"PostgreSQL di test non raggiungibile: {exc}")
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(_schema: None) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
