"""Deterministic, exit-code-based quality gate for agentic deliverables.

The LLM reviewer in :mod:`app.services.agent.worker_agent` can be optimistic —
it grades its own homework. This gate runs *real* tooling on the job folder and
gates delivery on the exit code, so a deliverable can only pass if it actually
compiles/builds:

- Python: ``py_compile`` every ``.py`` (syntax) and, when ``ruff`` is available,
  the high-confidence pyflakes error subset (undefined names, syntax, broken
  comparisons) — not style nags.
- Node: when ``package.json`` has a ``build`` script and ``node_modules`` is
  present, run ``npm run build`` and check the exit code. A TypeScript project
  with ``tsc`` available is type-checked with ``tsc --noEmit``.

Checks that cannot run (tool missing, deps not installed) are recorded as
*skipped* and never fail the gate — the goal is high-signal blocking, not
flakiness. A folder with nothing checkable passes (e.g. writing/SEO jobs, whose
quality is judged by the LLM reviewer instead).
"""

import json
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Directories we never scan or run tooling inside.
_IGNORED_DIRS = frozenset(
    {".git", ".venv", "venv", "env", "__pycache__", "node_modules", "dist", "build", ".claude", "qa", "qa_reports"}
)

# Pyflakes/syntax error subset (the classic flake8 CI gate): undefined names,
# syntax errors, broken comparisons, misplaced statements. Low false positives.
_RUFF_ERROR_SELECT = "E9,F63,F7,F82"


@dataclass(frozen=True)
class GateCheck:
    name: str
    status: str  # "passed" | "failed" | "skipped"
    detail: str

    @property
    def failed(self) -> bool:
        return self.status == "failed"


@dataclass
class GateResult:
    checks: list[GateCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(check.failed for check in self.checks)

    @property
    def failures(self) -> list[str]:
        return [f"{check.name}: {check.detail}" for check in self.checks if check.failed]

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "checks": [{"name": c.name, "status": c.status, "detail": c.detail} for c in self.checks],
        }


def run_quality_gate(folder: Path, *, timeout: int = 180) -> GateResult:
    """Run deterministic build/compile checks on ``folder`` and return a verdict."""
    result = GateResult()
    py_files = _collect_python_files(folder)
    if py_files:
        result.checks.append(_check_py_compile(folder, py_files, timeout))
        result.checks.append(_check_ruff(folder, timeout))

    package_json = folder / "package.json"
    if package_json.is_file():
        result.checks.extend(_check_node(folder, package_json, timeout))

    if not result.checks:
        result.checks.append(
            GateCheck("no_automated_checks", "skipped", "No compilable code found; relying on the LLM reviewer.")
        )
    return result


def _collect_python_files(folder: Path) -> list[Path]:
    files: list[Path] = []
    for path in folder.rglob("*.py"):
        if any(part in _IGNORED_DIRS for part in path.relative_to(folder).parts):
            continue
        files.append(path)
    return files


def _run(cmd: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess[str] | None:
    """Run a subprocess, returning None if it could not be launched."""
    try:
        return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, returncode=124, stdout="", stderr=f"timed out after {timeout}s")
    except OSError as exc:  # pragma: no cover - launch failure is environment-specific
        logger.warning("Quality-gate command failed to launch: %s (%s)", cmd, exc)
        return None


def _check_py_compile(folder: Path, py_files: list[Path], timeout: int) -> GateCheck:
    rel = [str(p.relative_to(folder)) for p in py_files]
    completed = _run([sys.executable, "-m", "py_compile", *rel], folder, timeout)
    if completed is None:
        return GateCheck("python_compile", "skipped", "Could not launch py_compile.")
    if completed.returncode == 0:
        return GateCheck("python_compile", "passed", f"{len(rel)} Python file(s) compile.")
    return GateCheck("python_compile", "failed", (completed.stderr or completed.stdout or "syntax error").strip()[:1500])


def _check_ruff(folder: Path, timeout: int) -> GateCheck:
    ruff = shutil.which("ruff")
    if ruff is None:
        return GateCheck("ruff_errors", "skipped", "ruff not installed.")
    completed = _run([ruff, "check", "--select", _RUFF_ERROR_SELECT, "--no-cache", "."], folder, timeout)
    if completed is None:
        return GateCheck("ruff_errors", "skipped", "Could not launch ruff.")
    if completed.returncode == 0:
        return GateCheck("ruff_errors", "passed", f"No {_RUFF_ERROR_SELECT} errors.")
    return GateCheck("ruff_errors", "failed", (completed.stdout or completed.stderr or "ruff errors").strip()[:1500])


def _check_node(folder: Path, package_json: Path, timeout: int) -> list[GateCheck]:
    checks: list[GateCheck] = []
    try:
        manifest = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [GateCheck("package_json_valid", "failed", f"package.json is not valid JSON: {exc}")]

    scripts = manifest.get("scripts") or {}
    deps_installed = (folder / "node_modules").is_dir()

    if "build" in scripts:
        if not deps_installed:
            checks.append(GateCheck("node_build", "skipped", "node_modules missing; cannot run npm build."))
        else:
            npm = shutil.which("npm")
            if npm is None:
                checks.append(GateCheck("node_build", "skipped", "npm not installed."))
            else:
                completed = _run([npm, "run", "build"], folder, timeout)
                if completed is None:
                    checks.append(GateCheck("node_build", "skipped", "Could not launch npm."))
                elif completed.returncode == 0:
                    checks.append(GateCheck("node_build", "passed", "npm run build succeeded."))
                else:
                    checks.append(
                        GateCheck("node_build", "failed", (completed.stderr or completed.stdout or "build failed").strip()[-1500:])
                    )

    if (folder / "tsconfig.json").is_file() and deps_installed:
        tsc = folder / "node_modules" / ".bin" / ("tsc.cmd" if sys.platform == "win32" else "tsc")
        if tsc.exists():
            completed = _run([str(tsc), "--noEmit"], folder, timeout)
            if completed is None:
                checks.append(GateCheck("typescript_typecheck", "skipped", "Could not launch tsc."))
            elif completed.returncode == 0:
                checks.append(GateCheck("typescript_typecheck", "passed", "tsc --noEmit clean."))
            else:
                checks.append(
                    GateCheck("typescript_typecheck", "failed", (completed.stdout or completed.stderr or "type errors").strip()[:1500])
                )
    return checks
