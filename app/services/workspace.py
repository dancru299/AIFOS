import re
from dataclasses import dataclass
from pathlib import Path

from app.core.config import Settings
from app.models import Job, TaskScope


@dataclass(frozen=True)
class WorkspacePaths:
    root: Path
    inputs: Path
    src: Path
    qa_reports: Path


class WorkspaceService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_for_job(self, job: Job) -> WorkspacePaths:
        storage_root = self.settings.resolved_workspace_storage_path
        workspace_root = (storage_root / _safe_segment(job.id)).resolve()

        if not workspace_root.is_relative_to(storage_root.resolve()):
            raise ValueError("Resolved workspace path escaped the configured storage root.")

        paths = WorkspacePaths(
            root=workspace_root,
            inputs=workspace_root / "inputs",
            src=workspace_root / "src",
            qa_reports=workspace_root / "qa_reports",
        )
        for path in (paths.inputs, paths.src, paths.qa_reports):
            path.mkdir(parents=True, exist_ok=True)
        return paths

    def write_pm_brief(self, job: Job, paths: WorkspacePaths, task_scope: TaskScope, instructions: str | None) -> Path:
        brief = _render_pm_brief(job, task_scope, instructions)
        brief_path = paths.inputs / "pm_brief.md"
        brief_path.write_text(brief, encoding="utf-8")
        return brief_path


def _safe_segment(value: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip(".-")
    return safe or "job"


def _render_pm_brief(job: Job, task_scope: TaskScope, instructions: str | None) -> str:
    stack = ", ".join(job.tech_stack or []) or "unknown"
    return (
        f"# PM Brief: {job.title}\n\n"
        f"- Job ID: {job.id}\n"
        f"- Source: {job.source}\n"
        f"- URL: {job.external_url}\n"
        f"- Task scope: {task_scope.value}\n"
        f"- Budget: {job.budget_estimate or job.budget_raw or 'unknown'}\n"
        f"- Client country: {job.client_country or job.client_location or 'unknown'}\n"
        f"- Tech stack: {stack}\n\n"
        "## Client Request\n"
        f"{job.description_raw.strip()}\n\n"
        "## Proposal Sent\n"
        f"{job.proposal_text or 'No proposal stored yet.'}\n\n"
        "## Extra Operator Instructions\n"
        f"{(instructions or 'None').strip()}\n"
    )
