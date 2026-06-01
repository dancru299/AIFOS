"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-01
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("external_url", sa.String(length=2048), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description_raw", sa.Text(), nullable=False),
        sa.Column("budget_raw", sa.String(length=255)),
        sa.Column("client_location", sa.String(length=255)),
        sa.Column("client_metadata", sa.JSON()),
        sa.Column("roi_score", sa.Float()),
        sa.Column("is_good_job", sa.Boolean()),
        sa.Column("budget_estimate", sa.String(length=255)),
        sa.Column("tech_stack", sa.JSON()),
        sa.Column("client_country", sa.String(length=255)),
        sa.Column("analysis_reasoning", sa.Text()),
        sa.Column("proposal_text", sa.Text()),
        sa.Column("proposal_price", sa.String(length=255)),
        sa.Column("proposal_timeline", sa.String(length=255)),
        sa.Column("workspace_path", sa.String(length=2048)),
        sa.Column("delivery_path", sa.String(length=2048)),
        sa.Column("telegram_chat_id", sa.String(length=64)),
        sa.Column("telegram_alert_message_id", sa.Integer()),
        sa.Column("last_error", sa.Text()),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("proposal_generated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("external_url", name="uq_jobs_external_url"),
    )

    op.create_table(
        "project_tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("task_title", sa.String(length=255), nullable=False),
        sa.Column("task_scope", sa.String(length=16), nullable=False),
        sa.Column("generated_output", sa.Text()),
        sa.Column("qa_status", sa.String(length=16), nullable=False, server_default="unreviewed"),
        sa.Column("qa_logs", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("project_tasks")
    op.drop_table("jobs")
