"""Startup recovery for jobs left mid-flight by a crash or restart.

``BackgroundTasks``/Arq workers can die while a job sits in a transitional
state (``analyzing``, ``generating_proposal``, ``in_progress``, ``qa_running``).
Without recovery those jobs are stuck forever. On startup we re-drive the ones
that are safe to resume automatically and park the heavier ones in a resting
state the operator can re-trigger from Telegram.
"""

import logging

from sqlalchemy import select

from app.db import session_scope
from app.models import Job, JobStatus
from app.services.pipeline import analyze_job, process_approved_job
from app.services.tasks import enqueue

logger = logging.getLogger(__name__)

# States that mean a worker was running when the process stopped.
_TRANSITIONAL = (
    JobStatus.ANALYZING,
    JobStatus.GENERATING_PROPOSAL,
    JobStatus.IN_PROGRESS,
    JobStatus.QA_RUNNING,
)


async def recover_stuck_jobs() -> list[str]:
    """Reset transitional jobs and re-enqueue the ones that can resume automatically."""
    recovered: list[str] = []
    to_reanalyze: list[str] = []
    to_regenerate: list[str] = []

    with session_scope() as db:
        jobs = db.scalars(select(Job).where(Job.status.in_(_TRANSITIONAL))).all()
        for job in jobs:
            previous = job.status
            job.last_error = "recovered_after_restart"

            if previous == JobStatus.ANALYZING:
                # Analysis is idempotent and cheap: rewind to pending and re-run.
                job.status = JobStatus.PENDING
                to_reanalyze.append(job.id)
            elif previous == JobStatus.GENERATING_PROPOSAL:
                # Keep the status; the proposal pipeline resumes from here.
                to_regenerate.append(job.id)
            else:
                # IN_PROGRESS / QA_RUNNING: sandbox work is heavy and may have
                # written partial output. Park it so the operator re-triggers.
                job.status = JobStatus.WORK_FAILED

            recovered.append(job.id)
            logger.warning("Recovered stuck job %s from %s", job.id, previous.value)

    for job_id in to_reanalyze:
        await enqueue(analyze_job, job_id)
    for job_id in to_regenerate:
        await enqueue(process_approved_job, job_id, None, None, None)

    if recovered:
        logger.info("Recovered %s stuck job(s) on startup", len(recovered))
    return recovered
