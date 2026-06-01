from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db import get_db
from app.models import Job, JobStatus
from app.schemas import TelegramWebhookUpdate
from app.services.pipeline import process_approved_job, process_rejected_job, process_started_work
from app.services.tasks import enqueue
from app.services.telegram import TelegramService
from app.state_machine import transition_job

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


def _verify_webhook_secret(settings: Settings, secret_token: str | None) -> None:
    if not settings.telegram_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram webhook secret is not configured.",
        )
    if not secret_token or secret_token != settings.telegram_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram webhook secret.",
        )


def _parse_callback_data(data: str) -> tuple[str | None, str | None]:
    if data.startswith("approve_"):
        return "approve", data.removeprefix("approve_")
    if data.startswith("dismiss_"):
        return "reject", data.removeprefix("dismiss_")
    if data.startswith("start_"):
        return "start", data.removeprefix("start_")
    if data.startswith("github_pr_"):
        return "github_pr", data.removeprefix("github_pr_")
    if data.startswith("approve:"):
        return "approve", data.removeprefix("approve:")
    if data.startswith("reject:"):
        return "reject", data.removeprefix("reject:")
    if data.startswith("dismiss:"):
        return "reject", data.removeprefix("dismiss:")
    if data.startswith("start:"):
        return "start", data.removeprefix("start:")
    return None, None


@router.post("/webhook")
async def telegram_webhook(
    payload: TelegramWebhookUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    secret_token: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    _verify_webhook_secret(settings, secret_token)

    callback = payload.callback_query
    if not callback or not callback.data:
        return {"ok": True, "ignored": True}

    action, job_id = _parse_callback_data(callback.data)
    if not action or not job_id:
        return {"ok": True, "ignored": True}

    job = db.get(Job, job_id)
    if not job:
        return {"ok": True, "ignored": True, "detail": "job_not_found"}

    callback_chat_id = callback.message.chat.id if callback.message else None
    callback_message_id = callback.message.message_id if callback.message else None

    if action == "approve":
        if job.status == JobStatus.AWAITING_HUMAN_REVIEW:
            transition_job(job, JobStatus.GENERATING_PROPOSAL)
            job.last_error = None
            db.commit()
            await enqueue(
                process_approved_job,
                job.id,
                callback.id,
                callback_chat_id,
                callback_message_id,
                background_tasks=background_tasks,
            )
            return {"ok": True, "status": job.status.value}

        if callback.id:
            background_tasks.add_task(TelegramService(settings).answer_callback_query, callback.id, "Already processing.")
        return {"ok": True, "status": job.status.value, "detail": "already_processed"}

    if action == "reject":
        if job.status == JobStatus.AWAITING_HUMAN_REVIEW:
            transition_job(job, JobStatus.REJECTED)
            job.last_error = None
            db.commit()
            await enqueue(
                process_rejected_job,
                job.id,
                callback.id,
                callback_chat_id,
                callback_message_id,
                background_tasks=background_tasks,
            )
            return {"ok": True, "status": job.status.value}

        if callback.id:
            background_tasks.add_task(TelegramService(settings).answer_callback_query, callback.id, "Already processed.")
        return {"ok": True, "status": job.status.value, "detail": "already_processed"}

    if action == "start":
        if job.status in {JobStatus.PROPOSAL_READY, JobStatus.QA_FAILED, JobStatus.WORK_FAILED, JobStatus.DELIVERY_READY}:
            transition_job(job, JobStatus.IN_PROGRESS)
            job.last_error = None
            db.commit()
            if callback.id:
                background_tasks.add_task(TelegramService(settings).answer_callback_query, callback.id, "Starting sandbox work...")
            await enqueue(
                process_started_work,
                job.id,
                None,
                None,
                None,
                callback_chat_id,
                background_tasks=background_tasks,
            )
            return {"ok": True, "status": job.status.value}

        if callback.id:
            background_tasks.add_task(TelegramService(settings).answer_callback_query, callback.id, "Work is already running or not ready.")
        return {"ok": True, "status": job.status.value, "detail": "work_not_started"}

    if action == "github_pr":
        if callback.id:
            background_tasks.add_task(TelegramService(settings).answer_callback_query, callback.id, "GitHub PR delivery is not implemented yet.")
        return {"ok": True, "status": job.status.value, "detail": "github_pr_not_implemented"}

    return {"ok": True, "ignored": True}
