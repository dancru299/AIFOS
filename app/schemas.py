from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models import JobStatus, TaskScope


class JobIngestRequest(BaseModel):
    source: Literal["upwork", "linkedin", "reddit", "x", "rss", "weworkremotely", "remoteok", "hackernews"]
    external_url: str = Field(min_length=1, max_length=2048)
    title: str = Field(min_length=1, max_length=512)
    description_raw: str = Field(min_length=1)
    budget_raw: str | None = Field(default=None, max_length=255)
    client_location: str | None = Field(default=None, max_length=255)
    client_metadata: dict[str, Any] | None = None


class JobIngestResponse(BaseModel):
    job_id: str
    status: JobStatus
    accepted: bool = True


class JobRead(BaseModel):
    id: str
    source: str
    external_url: str
    title: str
    budget_raw: str | None
    client_location: str | None
    roi_score: float | None
    is_good_job: bool | None
    budget_estimate: str | None
    tech_stack: list[str] | None
    client_country: str | None
    analysis_reasoning: str | None
    proposal_text: str | None
    proposal_price: str | None
    proposal_timeline: str | None
    workspace_path: str | None
    delivery_path: str | None
    status: JobStatus
    last_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TelegramChat(BaseModel):
    id: int | str


class TelegramMessage(BaseModel):
    message_id: int
    chat: TelegramChat


class TelegramUser(BaseModel):
    id: int | str


class TelegramCallbackQuery(BaseModel):
    id: str
    from_: TelegramUser = Field(alias="from")
    data: str | None = None
    message: TelegramMessage | None = None


class TelegramWebhookUpdate(BaseModel):
    update_id: int | None = None
    callback_query: TelegramCallbackQuery | None = None


class JobStartWorkRequest(BaseModel):
    task_scope: TaskScope | None = None
    task_title: str | None = Field(default=None, max_length=255)
    instructions: str | None = None


class JobStartWorkResponse(BaseModel):
    job_id: str
    status: JobStatus
    workspace_path: str | None = None
    accepted: bool = True


class HealthResponse(BaseModel):
    status: str
