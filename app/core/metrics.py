"""Prometheus metrics rendering.

Imported lazily by the ``/metrics`` endpoint so ``prometheus-client`` is only
required when metrics are enabled (``AIFOS_METRICS_ENABLED=true``).
"""

from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest
from sqlalchemy import func, select

from app.db import session_scope
from app.models import Job

_JOBS_BY_STATUS = Gauge("aifos_jobs", "Number of jobs by current status", ["status"])


def render_metrics() -> tuple[bytes, str]:
    with session_scope() as db:
        rows = db.execute(select(Job.status, func.count()).group_by(Job.status)).all()

    for status, count in rows:
        _JOBS_BY_STATUS.labels(status=status.value).set(count)

    return generate_latest(), CONTENT_TYPE_LATEST
