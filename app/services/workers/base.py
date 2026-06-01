from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import logging

from app.core.config import Settings
from app.models import Job, ProjectTask
from app.services.llm import LLMTextService, load_json_object
from app.services.workspace import WorkspacePaths


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeneratedFile:
    relative_path: str
    content: str


@dataclass(frozen=True)
class WorkerContext:
    job: Job
    task: ProjectTask
    workspace: WorkspacePaths
    attempt: int
    previous_qa_report: dict | None = None
    instructions: str | None = None


@dataclass(frozen=True)
class WorkerResult:
    files: list[GeneratedFile]
    summary: str


class BaseWorker(ABC):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @abstractmethod
    async def generate(self, context: WorkerContext) -> WorkerResult:
        raise NotImplementedError

    async def generate_with_llm(self, system_prompt: str, user_prompt: str) -> WorkerResult | None:
        try:
            content = await LLMTextService(self.settings, self.settings.worker_provider).generate_text(
                system_prompt,
                user_prompt,
                temperature=0.35,
            )
            payload = load_json_object(content)
            return _worker_result_from_payload(payload)
        except Exception:
            if not self.settings.allow_mock_llm:
                raise
            logger.exception("Worker LLM generation failed; falling back to local scaffold.")
            return None

    def write_files(self, workspace_src: Path, result: WorkerResult) -> list[Path]:
        written_files: list[Path] = []
        src_root = workspace_src.resolve()
        for generated_file in result.files:
            target = (workspace_src / generated_file.relative_path).resolve()
            if not target.is_relative_to(src_root):
                raise ValueError(f"Generated file escaped src workspace: {generated_file.relative_path}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(generated_file.content, encoding="utf-8")
            written_files.append(target)
        return written_files


def _worker_result_from_payload(payload: dict) -> WorkerResult:
    files_payload = payload.get("files")
    if not isinstance(files_payload, list) or not files_payload:
        raise ValueError(f"Worker response did not include files: {payload}")

    files: list[GeneratedFile] = []
    for item in files_payload:
        if not isinstance(item, dict):
            raise ValueError(f"Worker file entry must be an object: {item}")
        relative_path = str(item.get("path") or item.get("relative_path") or "").strip()
        content = str(item.get("content") or "")
        if not relative_path or not content:
            raise ValueError(f"Worker file entry missing path/content: {item}")
        files.append(GeneratedFile(relative_path=relative_path, content=content))

    return WorkerResult(
        files=files,
        summary=str(payload.get("summary") or "Generated worker files.").strip(),
    )
