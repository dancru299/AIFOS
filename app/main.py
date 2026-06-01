from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.admin import router as admin_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.system import router as system_router
from app.api.routes.telegram import router as telegram_router
from app.core.config import get_settings
from app.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, lifespan=lifespan)

    application.include_router(system_router)
    application.include_router(admin_router)
    application.include_router(jobs_router)
    application.include_router(telegram_router)
    return application


app = create_app()
