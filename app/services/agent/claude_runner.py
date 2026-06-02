"""Run Claude Code headless inside a folder and parse the result.

Uses the installed ``claude`` CLI (subprocess) so it reuses the existing CLI
login — no separate API key required. The call is blocking (a job run takes
minutes), so it runs in a worker thread via ``asyncio.to_thread`` to avoid
platform-specific async-subprocess issues (notably on Windows).
"""

import asyncio
import json
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from app.services.agent.guardrail import ALLOWED_TOOLS, DISALLOWED_TOOL_RULES

logger = logging.getLogger(__name__)


def _install_guardrail_hook(folder: Path) -> None:
    """Write a project ``.claude/settings.json`` that runs guard_hook.py before
    every Bash call, so destructive commands are denied even under
    bypassPermissions. Best-effort: a write failure must not abort the run."""
    hook_script = Path(__file__).resolve().parent / "guard_hook.py"
    settings = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {"type": "command", "command": f'"{sys.executable}" "{hook_script}"'}
                    ],
                }
            ]
        }
    }
    try:
        claude_dir = folder / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        (claude_dir / "settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    except OSError:
        logger.warning("Could not install guardrail hook in %s; continuing", folder, exc_info=True)


@dataclass
class AgentRun:
    ok: bool
    result_text: str = ""
    num_turns: int = 0
    cost_usd: float | None = None
    error: str | None = None
    events: list[dict] = field(default_factory=list)


async def run_claude_code(
    *,
    prompt: str,
    folder: Path,
    claude_bin: str = "claude",
    max_turns: int = 60,
    timeout_seconds: int = 1800,
    permission_mode: str = "bypassPermissions",
    enforce_guardrail_hook: bool = False,
) -> AgentRun:
    """Drive Claude Code over a single task in ``folder`` and return the result."""
    exe = shutil.which(claude_bin) or claude_bin
    if shutil.which(claude_bin) is None and not Path(claude_bin).exists():
        return AgentRun(ok=False, error=f"Claude Code CLI not found: {claude_bin}")

    folder.mkdir(parents=True, exist_ok=True)

    # bypassPermissions ignores the allow/deny lists, so a PreToolUse hook is the
    # only way to enforce the deny policy at runtime. Opt-in via settings.
    if enforce_guardrail_hook and permission_mode == "bypassPermissions":
        _install_guardrail_hook(folder)

    args = [
        exe,
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--permission-mode",
        permission_mode,
    ]
    # bypassPermissions ignores allow/deny lists (and is the only headless mode
    # that runs shell commands on Windows). For stricter modes, enforce the
    # allow/deny command lists — passed variadically (each tool as its own arg).
    if permission_mode != "bypassPermissions":
        args += ["--allowedTools", *ALLOWED_TOOLS, "--disallowedTools", *DISALLOWED_TOOL_RULES]
    args += ["--add-dir", str(folder), "--max-turns", str(max_turns)]

    try:
        completed = await asyncio.to_thread(
            subprocess.run,
            args,
            cwd=str(folder),
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return AgentRun(ok=False, error=f"Claude Code run timed out after {timeout_seconds}s")
    except Exception as exc:  # pragma: no cover - environment/exec failures
        logger.exception("Failed to launch Claude Code")
        return AgentRun(ok=False, error=str(exc))

    run = _parse_stream(completed.stdout, completed.stderr, completed.returncode)
    cost = f"${run.cost_usd:.4f}" if run.cost_usd is not None else "n/a"
    logger.info(
        "Claude Code run finished: ok=%s turns=%s cost=%s folder=%s",
        run.ok, run.num_turns, cost, folder.name,
    )
    return run


def _parse_stream(stdout: str, stderr: str, returncode: int) -> AgentRun:
    events: list[dict] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    result_event = next((e for e in reversed(events) if e.get("type") == "result"), None)
    if result_event is None:
        return AgentRun(
            ok=returncode == 0,
            error=(stderr or "No result event from Claude Code").strip() or None,
            events=events,
        )

    is_error = bool(result_event.get("is_error")) or result_event.get("subtype") != "success"
    return AgentRun(
        ok=not is_error,
        result_text=str(result_event.get("result", "")).strip(),
        num_turns=int(result_event.get("num_turns", 0) or 0),
        cost_usd=result_event.get("total_cost_usd"),
        error=None if not is_error else str(result_event.get("subtype") or "error"),
        events=events,
    )
