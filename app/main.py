from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.admin import router as admin_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.system import router as system_router
from app.api.routes.telegram import router as telegram_router
from app.core.config import get_settings
from app.core.logging import RequestIdMiddleware, configure_logging
from app.db import init_db
from app.services.recovery import recover_stuck_jobs
from app.services.tasks import close_arq_pool


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    await recover_stuck_jobs()
    yield
    await close_arq_pool()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.json_logs)
    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.add_middleware(RequestIdMiddleware)

    application.include_router(system_router)
    application.include_router(admin_router)
    application.include_router(jobs_router)
    application.include_router(telegram_router)
    return application


app = create_app()
