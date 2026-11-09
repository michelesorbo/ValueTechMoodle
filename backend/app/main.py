from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import courses, health, scorm
from app.core.config import get_settings
from app.core.db import engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = APIRouter(prefix="/api")
    api.include_router(health.router)
    api.include_router(courses.router)
    api.include_router(scorm.router)
    app.include_router(api)

    # Contenuti SCORM serviti dallo stesso origin del frontend (via reverse proxy)
    # così l'SCO nell'iframe può raggiungere window.parent.API / API_1484_11.
    settings.scorm_storage_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        scorm.SCORM_CONTENT_PREFIX,
        StaticFiles(directory=settings.scorm_storage_dir),
        name="scorm-content",
    )
    return app


app = create_app()
