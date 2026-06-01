import json

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import text

from app.core.config import get_settings
from app.db import engine
from app.schemas import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/healthz", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/deep")
async def deep_healthcheck() -> Response:
    settings = get_settings()
    checks: dict[str, str] = {"database": _check_database()}

    if settings.task_backend.lower() == "arq":
        checks["redis"] = await _check_redis(settings.redis_url)

    healthy = all(value == "ok" for value in checks.values())
    payload = {"status": "ok" if healthy else "degraded", "checks": checks}
    return Response(
        content=json.dumps(payload),
        media_type="application/json",
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@router.get("/metrics")
def metrics() -> Response:
    if not get_settings().metrics_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metrics are disabled.")

    from app.core.metrics import render_metrics

    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)


def _check_database() -> str:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:  # pragma: no cover - exercised only on real outages
        return f"error: {exc}"


async def _check_redis(redis_url: str) -> str:
    try:
        from redis.asyncio import Redis

        client = Redis.from_url(redis_url)
        try:
            await client.ping()
        finally:
            await client.aclose()
        return "ok"
    except Exception as exc:  # pragma: no cover - exercised only on real outages
        return f"error: {exc}"
