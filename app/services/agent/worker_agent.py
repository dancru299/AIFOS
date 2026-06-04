"""Plan / execute / review steps for the autonomous Claude Code worker.

Each step builds a focused prompt and drives Claude Code in the job folder via
:func:`run_claude_code`. The review step returns a structured verdict so the
pipeline can decide pass / repair / hand-off.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from app.core.config import Settings
from app.models import Job
from app.services.agent.claude_runner import AgentRun, run_claude_code
from app.services.llm import load_json_object

logger = logging.getLogger(__name__)

PASS_THRESHOLD = 90


@dataclass
class ReviewResult:
    completion_percent: int
    passed: bool
    summary: str
    blockers: list[str]
    checklist: list[dict]
    raw: dict
    cost_usd: float | None = None


async def plan(job: Job, folder: Path, settings: Settings) -> AgentRun:
    prompt = (
        "You are an autonomous freelance engineer. The current folder is your workspace.\n"
        "Read BRIEF.md (client request, the proposal we sent, and operator instructions).\n"
        "Produce a concrete, step-by-step implementation plan and WRITE IT to PLAN.md.\n"
        "PLAN.md must cover: deliverables, tech approach, file layout, the exact commands you\n"
        "will use to build and TEST the work, and how you will verify it meets the brief.\n"
        "Do NOT implement anything yet — only study the brief and write PLAN.md.\n"
        "Finish once PLAN.md exists."
    )
    return await run_claude_code(
        prompt=prompt,
        folder=folder,
        claude_bin=settings.claude_bin,
        permission_mode=settings.agent_permission_mode,
        max_turns=min(settings.agent_max_turns, 20),
        timeout_seconds=settings.agent_run_timeout_seconds,
        enforce_guardrail_hook=settings.agent_enforce_guardrail_hook,
    )


async def execute(job: Job, folder: Path, settings: Settings, previous_review: ReviewResult | None = None) -> AgentRun:
    repair = ""
    if previous_review is not None:
        repair = (
            "\nA previous QA review judged the work "
            f"{previous_review.completion_percent}% complete. Address these gaps:\n"
            + "\n".join(f"- {b}" for b in previous_review.blockers)
            + "\n"
        )
    prompt = (
        "You are an autonomous freelance engineer working in the current folder.\n"
        "Read BRIEF.md and PLAN.md, then FULLY implement the deliverable:\n"
        "- Write real, working code/content — not a scaffold or placeholders.\n"
        "- Actually run and TEST your work (build, run tests, execute scripts) and fix failures until it works.\n"
        "- Keep everything inside this folder. Never push to a remote.\n"
        "- Write SUMMARY.md: what you built, how to run it, and what you tested.\n"
        "- If blocked by something only the human can provide (credentials, access, an ambiguous\n"
        "  decision), record it in QUESTIONS.md and proceed with sensible assumptions where possible.\n"
        f"{repair}"
        "Deliver a finished, review-ready result (aim for >90% complete)."
    )
    return await run_claude_code(
        prompt=prompt,
        folder=folder,
        claude_bin=settings.claude_bin,
        permission_mode=settings.agent_permission_mode,
        max_turns=settings.agent_max_turns,
        timeout_seconds=settings.agent_run_timeout_seconds,
        enforce_guardrail_hook=settings.agent_enforce_guardrail_hook,
    )


async def review(job: Job, folder: Path, settings: Settings) -> ReviewResult:
    prompt = (
        "You are a strict senior QA reviewer. The current folder holds a freelance deliverable.\n"
        "Read BRIEF.md and PLAN.md, inspect the work, and where possible RUN the tests/build to\n"
        "verify it actually works. Then output ONLY a single JSON object as your final message\n"
        "(no prose, no markdown fences):\n"
        '{"completion_percent": <0-100 int>, "passed": <bool>, "summary": "<2-3 sentences>",\n'
        ' "checklist": [{"item": "...", "done": true}], "blockers": ["<missing or needs-human items>"]}'
    )
    run = await run_claude_code(
        prompt=prompt,
        folder=folder,
        claude_bin=settings.claude_bin,
        permission_mode=settings.agent_permission_mode,
        max_turns=min(settings.agent_max_turns, 20),
        timeout_seconds=settings.agent_run_timeout_seconds,
        enforce_guardrail_hook=settings.agent_enforce_guardrail_hook,
    )
    if not run.ok:
        return ReviewResult(
            completion_percent=0,
            passed=False,
            summary=f"Review run failed: {run.error}",
            blockers=[run.error or "review failed"],
            checklist=[],
            raw={},
            cost_usd=run.cost_usd,
        )
    result = _review_from_text(run.result_text)
    result.cost_usd = run.cost_usd
    return result


def _review_from_text(text: str) -> ReviewResult:
    try:
        payload = load_json_object(text)
    except Exception:
        return ReviewResult(
            completion_percent=0,
            passed=False,
            summary="Could not parse reviewer output.",
            blockers=["reviewer did not return valid JSON"],
            checklist=[],
            raw={"text": text},
        )

    try:
        completion = int(float(payload.get("completion_percent", 0)))
    except (TypeError, ValueError):
        completion = 0
    completion = max(0, min(100, completion))

    blockers = [str(b) for b in payload.get("blockers", []) if str(b).strip()]
    checklist = [c for c in payload.get("checklist", []) if isinstance(c, dict)]
    passed = bool(payload.get("passed")) and completion >= PASS_THRESHOLD

    return ReviewResult(
        completion_percent=completion,
        passed=passed,
        summary=str(payload.get("summary", "")).strip() or "No summary.",
        blockers=blockers,
        checklist=checklist,
        raw=payload,
    )
