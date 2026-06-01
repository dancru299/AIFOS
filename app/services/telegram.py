import json
import logging
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

import httpx

from app.core.config import Settings
from app.models import Job, ProjectTask, TaskScope
from app.services.http import request_with_retry

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessageRef:
    chat_id: str
    message_id: int


class TelegramService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def send_job_alert(self, job: Job) -> TelegramMessageRef | None:
        if not self.settings.telegram_enabled:
            logger.info("Telegram is not configured; skipping alert for job %s", job.id)
            return None

        payload = {
            "chat_id": self.settings.telegram_default_chat_id,
            "text": self._render_job_alert(job),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "\U0001F44D Approve & Pitch", "callback_data": f"approve_{job.id}"},
                        {"text": "\U0001F44E Dismiss", "callback_data": f"dismiss_{job.id}"},
                    ]
                ]
            },
        }
        data = await self._post("sendMessage", payload)
        if not data:
            return None
        result = data.get("result", {})
        return TelegramMessageRef(chat_id=str(result.get("chat", {}).get("id")), message_id=result.get("message_id"))

    async def send_generation_started(self, job: Job, chat_id: str | int | None = None) -> None:
        target_chat_id = self._resolve_chat_id(job, chat_id)
        if not self.settings.telegram_bot_token or not target_chat_id:
            logger.info("Telegram is not configured; skipping generation notice for job %s", job.id)
            return

        payload = {
            "chat_id": target_chat_id,
            "text": self._render_generation_started(job),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        await self._post("sendMessage", payload)

    async def send_proposal(self, job: Job, chat_id: str | int | None = None) -> None:
        target_chat_id = self._resolve_chat_id(job, chat_id)
        if not self.settings.telegram_bot_token or not target_chat_id:
            logger.info("Telegram is not configured; skipping proposal delivery for job %s", job.id)
            return

        payload = {
            "chat_id": target_chat_id,
            "text": self._render_proposal(job),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "\U0001F680 Start Work", "callback_data": f"start_{job.id}"},
                    ]
                ]
            },
        }
        await self._post("sendMessage", payload)

    async def send_proposal_failed(self, job: Job, chat_id: str | int | None = None) -> None:
        target_chat_id = self._resolve_chat_id(job, chat_id)
        if not self.settings.telegram_bot_token or not target_chat_id:
            logger.info("Telegram is not configured; skipping proposal failure notice for job %s", job.id)
            return

        payload = {
            "chat_id": target_chat_id,
            "text": self._render_proposal_failed(job),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        await self._post("sendMessage", payload)

    async def send_work_started(self, job: Job, task_scope: TaskScope, chat_id: str | int | None = None) -> None:
        target_chat_id = self._resolve_chat_id(job, chat_id)
        if not self.settings.telegram_bot_token or not target_chat_id:
            logger.info("Telegram is not configured; skipping work-start notice for job %s", job.id)
            return

        payload = {
            "chat_id": target_chat_id,
            "text": self._render_work_started(job, task_scope),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        await self._post("sendMessage", payload)

    async def send_delivery_ready(self, job: Job, task: ProjectTask, chat_id: str | int | None = None) -> None:
        target_chat_id = self._resolve_chat_id(job, chat_id)
        if not self.settings.telegram_bot_token or not target_chat_id:
            logger.info("Telegram is not configured; skipping delivery notice for job %s", job.id)
            return

        delivery_path = Path(job.delivery_path) if job.delivery_path else None
        caption = self._render_delivery_ready(job, task)
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "\U0001F680 GitHub PR (soon)", "callback_data": f"github_pr_{job.id}"},
                ]
            ]
        }
        if delivery_path and delivery_path.exists():
            await self._post_file(
                "sendDocument",
                {
                    "chat_id": target_chat_id,
                    "caption": caption,
                    "parse_mode": "HTML",
                    "reply_markup": reply_markup,
                },
                "document",
                delivery_path,
            )
            return

        payload = {
            "chat_id": target_chat_id,
            "text": caption,
            "parse_mode": "HTML",
            "reply_markup": reply_markup,
            "disable_web_page_preview": True,
        }
        await self._post("sendMessage", payload)

    async def send_work_failed(self, job: Job, reason: str, chat_id: str | int | None = None) -> None:
        target_chat_id = self._resolve_chat_id(job, chat_id)
        if not self.settings.telegram_bot_token or not target_chat_id:
            logger.info("Telegram is not configured; skipping work-failure notice for job %s", job.id)
            return

        payload = {
            "chat_id": target_chat_id,
            "text": self._render_work_failed(job, reason),
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        await self._post("sendMessage", payload)

    async def answer_callback_query(self, callback_query_id: str, text: str) -> None:
        if not self.settings.telegram_bot_token:
            return

        payload = {"callback_query_id": callback_query_id, "text": text, "show_alert": False}
        await self._post("answerCallbackQuery", payload)

    async def clear_inline_keyboard(self, chat_id: str | int | None, message_id: int | None) -> None:
        if not self.settings.telegram_bot_token or not chat_id or message_id is None:
            return

        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []},
        }
        await self._post("editMessageReplyMarkup", payload)

    async def _post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.telegram_bot_token:
            return {}

        url = f"{self.settings.telegram_api_base}/bot{self.settings.telegram_bot_token}/{method}"
        # Telegram is a best-effort notification side-channel: a failure here must
        # never abort the analysis/proposal/work pipeline that produces value.
        try:
            response = await request_with_retry("POST", url, json=payload, timeout=20.0)
            data = response.json()
        except Exception:
            logger.warning("Telegram %s request failed; continuing", method, exc_info=True)
            return {}
        if not data.get("ok", False):
            logger.warning("Telegram %s returned non-ok response: %s", method, data)
            return {}
        return data

    async def _post_file(self, method: str, payload: dict[str, Any], field_name: str, path: Path) -> dict[str, Any]:
        if not self.settings.telegram_bot_token:
            return {}

        url = f"{self.settings.telegram_api_base}/bot{self.settings.telegram_bot_token}/{method}"
        data_payload = {
            key: json_value(value)
            for key, value in payload.items()
            if value is not None
        }
        try:
            with path.open("rb") as handle:
                files = {field_name: (path.name, handle, "application/zip")}
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, data=data_payload, files=files)
                    response.raise_for_status()
                    data = response.json()
        except Exception:
            logger.warning("Telegram %s file upload failed; continuing", method, exc_info=True)
            return {}
        if not data.get("ok", False):
            logger.warning("Telegram %s returned non-ok response: %s", method, data)
            return {}
        return data

    def _resolve_chat_id(self, job: Job, fallback_chat_id: str | int | None = None) -> str | int | None:
        return fallback_chat_id or job.telegram_chat_id or self.settings.telegram_default_chat_id

    def _render_job_alert(self, job: Job) -> str:
        score = f"{job.roi_score:.1f}/10" if job.roi_score is not None else "n/a"
        budget = job.budget_estimate or job.budget_raw or "unknown"
        country = job.client_country or job.client_location or "unknown"
        stack = ", ".join(job.tech_stack or []) or "unknown"
        return (
            "<b>NEW HIGH-ROI JOB</b>\n\n"
            f"<b>{escape(job.title)}</b>\n\n"
            f"<b>Source:</b> {escape(job.source)}\n"
            f"<b>Budget:</b> {escape(budget)}\n"
            f"<b>Country:</b> {escape(country)}\n"
            f"<b>ROI:</b> {escape(score)}\n"
            f"<b>Stack:</b> {escape(stack)}\n\n"
            f"<b>Reasoning:</b>\n{escape(job.analysis_reasoning or 'n/a')}\n\n"
            f"<a href=\"{escape(job.external_url)}\">Open job</a>"
        )

    def _render_generation_started(self, job: Job) -> str:
        job_ref = job.id[:8]
        return (
            f"\U0001F504 Đang kích hoạt LLM để soạn thảo Proposal cho Job #{escape(job_ref)}...\n"
            f"<b>{escape(job.title)}</b>"
        )

    def _render_proposal(self, job: Job) -> str:
        proposal = escape(job.proposal_text or "")
        price = escape(job.proposal_price or "n/a")
        timeline = escape(job.proposal_timeline or "n/a")
        return (
            "<b>PROPOSAL READY</b>\n\n"
            f"<b>{escape(job.title)}</b>\n"
            f"<b>Estimated Bid:</b> {price}\n"
            f"<b>Timeline:</b> {timeline}\n\n"
            "<b>Copy proposal:</b>\n"
            f"<pre><code>{proposal}</code></pre>\n"
            f"<a href=\"{escape(job.external_url)}\">Open job</a>"
        ).strip()

    def _render_proposal_failed(self, job: Job) -> str:
        error = escape(job.last_error or "Unknown error")
        return (
            "<b>PROPOSAL FAILED</b>\n\n"
            f"<b>{escape(job.title)}</b>\n"
            f"<b>Error:</b> {error}"
        ).strip()

    def _render_work_started(self, job: Job, task_scope: TaskScope) -> str:
        return (
            f"\U0001F680 <b>Sandbox Engine started</b>\n\n"
            f"<b>Job:</b> {escape(job.title)}\n"
            f"<b>Scope:</b> {escape(task_scope.value)}\n"
            f"<b>Workspace:</b> <code>{escape(job.workspace_path or 'creating...')}</code>"
        ).strip()

    def _render_delivery_ready(self, job: Job, task: ProjectTask) -> str:
        qa_summary = escape(task.qa_logs or "QA passed.")
        if len(qa_summary) > 420:
            qa_summary = qa_summary[:420] + "..."
        return (
            f"\u2705 <b>JOB #{escape(job.id[:8])} HOÀN THÀNH TỰ ĐỘNG!</b>\n\n"
            f"<b>Loại công việc:</b> {escape(task.task_scope.value)}\n"
            f"<b>Kết quả QA:</b> PASSED\n"
            f"<b>File đầu ra:</b> <code>{escape(job.delivery_path or 'n/a')}</code>\n\n"
            f"<b>QA notes:</b>\n<code>{qa_summary}</code>"
        ).strip()

    def _render_work_failed(self, job: Job, reason: str) -> str:
        return (
            f"\u26A0\uFE0F <b>JOB #{escape(job.id[:8])} CẦN REVIEW</b>\n\n"
            f"<b>{escape(job.title)}</b>\n"
            f"<b>Status:</b> {escape(job.status.value)}\n"
            f"<b>Reason:</b> {escape(reason)}"
        ).strip()


def json_value(value: Any) -> str:
    if isinstance(value, dict | list):
        return json.dumps(value)
    return str(value)
