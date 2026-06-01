import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.models import QAStatus, TaskScope
from app.services.workspace import WorkspacePaths


@dataclass(frozen=True)
class QAResult:
    status: QAStatus
    summary: str
    report: dict[str, Any]

    @property
    def passed(self) -> bool:
        return self.status == QAStatus.PASSED


class QAService:
    def run(self, task_scope: TaskScope, workspace: WorkspacePaths, attempt: int) -> QAResult:
        checks: list[dict[str, Any]] = []

        if task_scope == TaskScope.WRITING:
            checks.extend(_check_writing(workspace.src))
        else:
            checks.extend(_check_code_or_scraping(task_scope, workspace.src))

        passed = all(check["passed"] for check in checks)
        status = QAStatus.PASSED if passed else QAStatus.FAILED
        summary = _build_summary(task_scope, checks, passed)
        report = {
            "attempt": attempt,
            "task_scope": task_scope.value,
            "status": status.value,
            "summary": summary,
            "checks": checks,
        }

        report_path = workspace.qa_reports / f"qa_report_attempt_{attempt}.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        latest_report_path = workspace.qa_reports / "qa_report.json"
        latest_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        return QAResult(status=status, summary=summary, report=report)


def _check_writing(src: Path) -> list[dict[str, Any]]:
    article_path = src / "article.md"
    if not article_path.exists():
        return [{"name": "article_exists", "passed": False, "detail": "article.md was not generated."}]

    text = article_path.read_text(encoding="utf-8")
    words = re.findall(r"\b[\w'-]+\b", text)
    headings = re.findall(r"^#{1,3}\s+", text, flags=re.MULTILINE)
    checks = [
        {
            "name": "article_word_count",
            "passed": len(words) >= 250,
            "detail": f"{len(words)} words; minimum is 250 for MVP QA.",
        },
        {
            "name": "heading_structure",
            "passed": len(headings) >= 4,
            "detail": f"{len(headings)} markdown headings found.",
        },
        {
            "name": "no_empty_sections",
            "passed": "TODO" not in text.upper(),
            "detail": "No TODO placeholders in article body.",
        },
    ]
    return checks


def _check_code_or_scraping(task_scope: TaskScope, src: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    generated_files = [path for path in src.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
    checks.append(
        {
            "name": "generated_files_exist",
            "passed": bool(generated_files),
            "detail": f"{len(generated_files)} source files generated.",
        }
    )

    py_files = [path for path in generated_files if path.suffix == ".py"]
    if task_scope == TaskScope.SCRAPING:
        checks.append(
            {
                "name": "crawler_py_exists",
                "passed": (src / "crawler.py").exists(),
                "detail": "crawler.py is required for scraping jobs.",
            }
        )

    if py_files:
        checks.append(_run_py_compile(src, py_files))

    if task_scope == TaskScope.CODE:
        checks.append(
            {
                "name": "web_entry_exists",
                "passed": (src / "index.html").exists() or any(path.suffix in {".tsx", ".jsx", ".php"} for path in generated_files),
                "detail": "Expected index.html, TSX/JSX, or PHP entrypoint.",
            }
        )

    return checks


def _run_py_compile(src: Path, py_files: list[Path]) -> dict[str, Any]:
    relative_files = [str(path.relative_to(src)) for path in py_files]
    completed = subprocess.run(
        [sys.executable, "-m", "py_compile", *relative_files],
        cwd=src,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    return {
        "name": "python_py_compile",
        "passed": completed.returncode == 0,
        "detail": (completed.stderr or completed.stdout or "Python syntax check passed.").strip(),
        "files": relative_files,
    }


def _build_summary(task_scope: TaskScope, checks: list[dict[str, Any]], passed: bool) -> str:
    failed = [check for check in checks if not check["passed"]]
    if passed:
        if task_scope == TaskScope.WRITING:
            return "PASSED: Markdown article has enough length, headings, and no TODO placeholders."
        if task_scope == TaskScope.SCRAPING:
            return "PASSED: crawler.py exists and Python syntax check passed."
        return "PASSED: web/code files were generated and entrypoint check passed."
    return "FAILED: " + "; ".join(f"{check['name']} - {check['detail']}" for check in failed)
