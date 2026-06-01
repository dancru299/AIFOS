"""Background task dispatch abstraction.

Routes and the startup recovery pass call :func:`enqueue` instead of touching
``BackgroundTasks`` or Arq directly. The backend is chosen by ``task_backend``:

- ``background`` (default): FastAPI ``BackgroundTasks`` when a request is in
  flight, otherwise a detached ``asyncio`` task. Zero infra; used by tests.
- ``arq``: enqueue onto a Redis-backed Arq queue so jobs survive restarts and
  get retried. The Arq worker (``app/worker_arq.py``) runs the same coroutines.

Pipeline coroutines are enqueued by name (``func.__name__``); the Arq worker
registers functions under those same names, so the two stay in sync.
"""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import BackgroundTasks

from app.core.config import get_settings

logger = logging.getLogger(__name__)

TaskFn = Callable[..., Coroutine[Any, Any, None]]

_arq_pool: Any = None
_background_set: set[asyncio.Task[Any]] = set()


async def enqueue(func: TaskFn, *args: Any, background_tasks: BackgroundTasks | None = None) -> None:
    """Schedule ``func(*args)`` to run outside the current request."""
    backend = get_settings().task_backend.lower()

    if backend == "arq":
        await _enqueue_arq(func, *args)
        return

    if background_tasks is not None:
        background_tasks.add_task(func, *args)
        return

    # No request context (e.g. startup recovery): run detached on the loop and
    # keep a reference so the task is not garbage-collected mid-flight.
    task: asyncio.Task[None] = asyncio.create_task(func(*args))
    _background_set.add(task)
    task.add_done_callback(_background_set.discard)


async def _enqueue_arq(func: TaskFn, *args: Any) -> None:
    pool = await _get_arq_pool()
    await pool.enqueue_job(func.__name__, *args)


async def _get_arq_pool() -> Any:
    global _arq_pool
    if _arq_pool is None:
        from arq import create_pool
        from arq.connections import RedisSettings

        _arq_pool = await create_pool(RedisSettings.from_dsn(get_settings().redis_url))
    return _arq_pool


async def close_arq_pool() -> None:
    global _arq_pool
    if _arq_pool is not None:
        await _arq_pool.aclose()
        _arq_pool = None
