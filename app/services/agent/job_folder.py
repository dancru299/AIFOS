"""Create and seed the per-job delivery folder the agent works in.

Each job gets ``<AIFOS_DELIVERY_ROOT>/<source>-<slug>-<shortid>/`` containing
``BRIEF.md`` (everything the agent needs to know). The agent then writes
``PLAN.md``, the real deliverable, ``SUMMARY.md`` and ``QUESTIONS.md`` here, and
this folder is what the operator opens to review — no ZIP.
"""

import re
from pathlib import Path

from app.core.config import Settings
from app.models import Job


def create_job_folder(job: Job, settings: Settings) -> Path:
    root = settings.resolved_delivery_root
    name = f"{_slug(job.source)}-{_slug(job.title)[:40]}-{job.id[:8]}"
    folder = (root / name).resolve()
    if not folder.is_relative_to(root):
        raise ValueError("Resolved job folder escaped the configured delivery root.")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def write_brief(job: Job, folder: Path, instructions: str | None) -> Path:
    stack = ", ".join(job.tech_stack or []) or "unknown"
    brief = (
        f"# BRIEF: {job.title}\n\n"
        f"- Job ID: {job.id}\n"
        f"- Source: {job.source}\n"
        f"- Original URL: {job.external_url}\n"
        f"- Budget: {job.budget_estimate or job.budget_raw or 'unknown'}\n"
        f"- Client country: {job.client_country or job.client_location or 'unknown'}\n"
        f"- Tech stack hints: {stack}\n\n"
        "## Client Request\n"
        f"{job.description_raw.strip()}\n\n"
        "## Proposal We Sent\n"
        f"{job.proposal_text or 'No proposal stored.'}\n\n"
        "## Operator Instructions\n"
        f"{(instructions or 'None').strip()}\n\n"
        "## Definition of Done\n"
        "A finished, review-ready deliverable that satisfies the client request, runs/builds\n"
        "without errors, and is tested. Leave clear run instructions in SUMMARY.md.\n"
    )
    brief_path = folder / "BRIEF.md"
    brief_path.write_text(brief, encoding="utf-8")
    return brief_path


def read_text_if_exists(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:limit] if limit else text


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip(".-").lower()
    return slug or "job"
