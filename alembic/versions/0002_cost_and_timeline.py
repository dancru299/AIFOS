"""add job cost total and status-transition timeline

Revision ID: 0002_cost_and_timeline
Revises: 0001_initial
Create Date: 2026-06-03
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_cost_and_timeline"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("total_cost_usd", sa.Float(), nullable=False, server_default="0"),
    )

    op.create_table(
        "job_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("from_status", sa.String(length=32)),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("detail", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_job_events_job_id", "job_events", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_job_events_job_id", table_name="job_events")
    op.drop_table("job_events")
    op.drop_column("jobs", "total_cost_usd")
