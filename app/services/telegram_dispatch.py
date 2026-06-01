"""Shared handling for Telegram inline-button callbacks.

Both the webhook route (push) and the long-poller (pull) decode a callback and
call :func:`dispatch_callback`, so the two delivery modes share identical logic.
The function manages its own DB transaction and enqueues the heavy pipeline work
through :func:`app.services.tasks.enqueue` (passing ``background_tasks`` when a
request is in flight, ``None`` from the poller).
"""

import logging
from typing import Any

from fastapi import BackgroundTasks

from app.core.config import Settings
from app.db import session_scope
from app.models import Job, JobStatus
from app.services.pipeline import process_approved_job, process_rejected_job, process_started_work
from app.services.tasks import enqueue
from app.services.telegram import TelegramService
from app.state_machine import transition_job

logger = logging.getLogger(__name__)

_START_WORK_STATES = {
    JobStatus.PROPOSAL_READY,
    JobStatus.QA_FAILED,
    JobStatus.WORK_FAILED,
    JobStatus.DELIVERY_READY,
}


def parse_callback_data(data: str) -> tuple[str | None, str | None]:
    for prefix, action in (
        ("approve_", "approve"),
        ("dismiss_", "reject"),
        ("reject_", "reject"),
        ("start_", "start"),
        ("github_pr_", "github_pr"),
        ("approve:", "approve"),
        ("dismiss:", "reject"),
        ("reject:", "reject"),
        ("start:", "start"),
    ):
        if data.startswith(prefix):
            return action, data.removeprefix(prefix)
    return None, None


async def dispatch_callback(
    *,
    data: str | None,
    callback_id: str | None,
    callback_chat_id: str | int | None,
    callback_message_id: int | None,
    settings: Settings,
    background_tasks: BackgroundTasks | None = None,
) -> dict[str, Any]:
    """Apply an inline-button decision: transition the job and enqueue work."""
    if not data:
        return {"ok": True, "ignored": True}
    action, job_id = parse_callback_data(data)
    if not action or not job_id:
        return {"ok": True, "ignored": True}

    # Decide the outcome inside a short transaction; defer enqueue/network to after.
    intent: str
    response: dict[str, Any]
    ack: str | None = None

    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None:
            return {"ok": True, "ignored": True, "detail": "job_not_found"}
        current = job.status

        if action == "approve" and current == JobStatus.AWAITING_HUMAN_REVIEW:
            transition_job(job, JobStatus.GENERATING_PROPOSAL)
            job.last_error = None
            intent, response = "approved", {"ok": True, "status": JobStatus.GENERATING_PROPOSAL.value}
        elif action == "reject" and current == JobStatus.AWAITING_HUMAN_REVIEW:
            transition_job(job, JobStatus.REJECTED)
            job.last_error = None
            intent, response = "rejected", {"ok": True, "status": JobStatus.REJECTED.value}
        elif action == "start" and current in _START_WORK_STATES:
            transition_job(job, JobStatus.IN_PROGRESS)
            job.last_error = None
            intent, response = "start", {"ok": True, "status": JobStatus.IN_PROGRESS.value}
        elif action in {"approve", "reject"}:
            intent, ack = "ack", "Already processed."
            response = {"ok": True, "status": current.value, "detail": "already_processed"}
        elif action == "start":
            intent, ack = "ack", "Work is already running or not ready."
            response = {"ok": True, "status": current.value, "detail": "work_not_started"}
        elif action == "github_pr":
            intent, ack = "ack", "GitHub PR delivery is not implemented yet."
            response = {"ok": True, "status": current.value, "detail": "github_pr_not_implemented"}
        else:
            return {"ok": True, "ignored": True}

    telegram = TelegramService(settings)

    if intent == "approved":
        await enqueue(process_approved_job, job_id, callback_id, callback_chat_id, callback_message_id, background_tasks=background_tasks)
    elif intent == "rejected":
        await enqueue(process_rejected_job, job_id, callback_id, callback_chat_id, callback_message_id, background_tasks=background_tasks)
    elif intent == "start":
        if callback_id:
            await telegram.answer_callback_query(callback_id, "Starting sandbox work...")
        await enqueue(process_started_work, job_id, None, None, None, callback_chat_id, background_tasks=background_tasks)
    elif intent == "ack" and callback_id and ack:
        await telegram.answer_callback_query(callback_id, ack)

    return response
