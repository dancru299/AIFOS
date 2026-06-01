"""Arq worker entrypoint.

Run with::

    arq app.worker_arq.WorkerSettings

Each task is a thin ``(ctx, *args)`` wrapper around a pipeline coroutine. The
function names here match the names used by ``app.services.tasks.enqueue``
(``func.__name__``), so enqueuing ``analyze_job`` runs ``analyze_job`` below.
"""

from typing import Any

from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db import init_db
from app.models import TaskScope
from app.services import pipeline


async def analyze_job(ctx: dict[str, Any], job_id: str) -> None:
    await pipeline.analyze_job(job_id)


async def process_approved_job(
    ctx: dict[str, Any],
    job_id: str,
    callback_query_id: str | None,
    callback_chat_id: str | int | None,
    callback_message_id: int | None,
) -> None:
    await pipeline.process_approved_job(job_id, callback_query_id, callback_chat_id, callback_message_id)


async def process_rejected_job(
    ctx: dict[str, Any],
    job_id: str,
    callback_query_id: str | None,
    callback_chat_id: str | int | None,
    callback_message_id: int | None,
) -> None:
    await pipeline.process_rejected_job(job_id, callback_query_id, callback_chat_id, callback_message_id)


async def process_started_work(
    ctx: dict[str, Any],
    job_id: str,
    task_scope: TaskScope | None = None,
    task_title: str | None = None,
    instructions: str | None = None,
    callback_chat_id: str | int | None = None,
) -> None:
    await pipeline.process_started_work(job_id, task_scope, task_title, instructions, callback_chat_id)


async def start_planning(
    ctx: dict[str, Any],
    job_id: str,
    instructions: str | None = None,
    callback_chat_id: str | int | None = None,
) -> None:
    await pipeline.start_planning(job_id, instructions, callback_chat_id)


async def execute_approved_plan(
    ctx: dict[str, Any],
    job_id: str,
    callback_chat_id: str | int | None = None,
) -> None:
    await pipeline.execute_approved_plan(job_id, callback_chat_id)


async def startup(ctx: dict[str, Any]) -> None:
    configure_logging(get_settings().json_logs)
    init_db()


class WorkerSettings:
    functions = [
        analyze_job,
        process_approved_job,
        process_rejected_job,
        process_started_work,
        start_planning,
        execute_approved_plan,
    ]
    on_startup = startup
    max_tries = 3
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
