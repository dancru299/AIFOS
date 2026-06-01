import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DISCARDED = "discarded"
    AWAITING_HUMAN_REVIEW = "awaiting_human_review"
    GENERATING_PROPOSAL = "generating_proposal"
    PROPOSAL_READY = "proposal_ready"
    PLANNING = "planning"
    AWAITING_PLAN_APPROVAL = "awaiting_plan_approval"
    IN_PROGRESS = "in_progress"
    QA_RUNNING = "qa_running"
    DELIVERY_READY = "delivery_ready"
    WORK_FAILED = "work_failed"
    QA_FAILED = "qa_failed"
    REJECTED = "rejected"
    ANALYSIS_FAILED = "analysis_failed"
    PROPOSAL_FAILED = "proposal_failed"


class TaskScope(str, enum.Enum):
    CODE = "code"
    WRITING = "writing"
    SCRAPING = "scraping"


class QAStatus(str, enum.Enum):
    UNREVIEWED = "unreviewed"
    PASSED = "passed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    external_url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description_raw: Mapped[str] = mapped_column(Text, nullable=False)
    budget_raw: Mapped[str | None] = mapped_column(String(255))
    client_location: Mapped[str | None] = mapped_column(String(255))
    client_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    roi_score: Mapped[float | None] = mapped_column(Float)
    is_good_job: Mapped[bool | None] = mapped_column(Boolean)
    budget_estimate: Mapped[str | None] = mapped_column(String(255))
    tech_stack: Mapped[list[str] | None] = mapped_column(JSON)
    client_country: Mapped[str | None] = mapped_column(String(255))
    analysis_reasoning: Mapped[str | None] = mapped_column(Text)
    proposal_text: Mapped[str | None] = mapped_column(Text)
    proposal_price: Mapped[str | None] = mapped_column(String(255))
    proposal_timeline: Mapped[str | None] = mapped_column(String(255))
    workspace_path: Mapped[str | None] = mapped_column(String(2048))
    delivery_path: Mapped[str | None] = mapped_column(String(2048))
    telegram_chat_id: Mapped[str | None] = mapped_column(String(64))
    telegram_alert_message_id: Mapped[int | None] = mapped_column(Integer)
    last_error: Mapped[str | None] = mapped_column(Text)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False),
        default=JobStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    proposal_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project_tasks: Mapped[list["ProjectTask"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class ProjectTask(Base):
    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), ForeignKey("jobs.id"), nullable=False)
    task_title: Mapped[str] = mapped_column(String(255), nullable=False)
    task_scope: Mapped[TaskScope] = mapped_column(Enum(TaskScope, native_enum=False), nullable=False)
    generated_output: Mapped[str | None] = mapped_column(Text)
    qa_status: Mapped[QAStatus] = mapped_column(
        Enum(QAStatus, native_enum=False),
        default=QAStatus.UNREVIEWED,
        nullable=False,
    )
    qa_logs: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    job: Mapped[Job] = relationship(back_populates="project_tasks")
