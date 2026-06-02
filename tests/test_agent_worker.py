import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.db import session_scope
from app.models import Job, JobStatus
from app.services import pipeline, telegram_dispatch
from app.services.agent import worker_agent
from app.services.agent.claude_runner import AgentRun
from app.services.agent.guardrail import is_command_blocked
from app.services.agent.job_folder import create_job_folder

GUARD_HOOK = Path(__file__).resolve().parents[1] / "app" / "services" / "agent" / "guard_hook.py"


def _run_guard_hook(payload: str) -> int:
    return subprocess.run(
        [sys.executable, str(GUARD_HOOK)],
        input=payload,
        capture_output=True,
        text=True,
    ).returncode


@pytest.fixture
def agent_env(client, tmp_path):
    """Switch settings to the claude_code engine with a throwaway delivery root."""
    os.environ["AIFOS_WORKER_ENGINE"] = "claude_code"
    os.environ["AIFOS_DELIVERY_ROOT"] = str(tmp_path / "deliveries")
    get_settings.cache_clear()
    try:
        yield
    finally:
        os.environ.pop("AIFOS_WORKER_ENGINE", None)
        os.environ.pop("AIFOS_DELIVERY_ROOT", None)
        os.environ.pop("AIFOS_AGENT_PLAN_GATE", None)
        get_settings.cache_clear()


def _make_job(url: str, status: JobStatus) -> str:
    with session_scope() as db:
        job = Job(
            source="upwork",
            external_url=url,
            title="Build a small Python utility",
            description_raw="Implement and test a small Python function.",
            status=status,
        )
        db.add(job)
        db.flush()
        return job.id


def _delete(job_id: str) -> None:
    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is not None:
            db.delete(job)


def test_guardrail_blocks_dangerous_commands():
    assert is_command_blocked("rm -rf /")
    assert is_command_blocked("sudo rm file")
    assert is_command_blocked("git push origin main")
    assert is_command_blocked("ssh user@host")
    assert not is_command_blocked("pip install requests")
    assert not is_command_blocked("python -m pytest -q")
    assert not is_command_blocked("npm install")


def test_guard_hook_blocks_dangerous_command_exit_2():
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}})
    assert _run_guard_hook(payload) == 2


def test_guard_hook_allows_safe_command_exit_0():
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "pytest -q"}})
    assert _run_guard_hook(payload) == 0


def test_guard_hook_fails_open_on_bad_input():
    assert _run_guard_hook("not json") == 0


async def test_start_planning_writes_plan_and_awaits_approval(agent_env, monkeypatch):
    async def fake_plan(job, folder, settings):
        (folder / "PLAN.md").write_text("# Plan\n1. Implement\n2. Test\n", encoding="utf-8")
        return AgentRun(ok=True, result_text="planned")

    monkeypatch.setattr(worker_agent, "plan", fake_plan)

    job_id = _make_job("https://ex.test/agent-plan", JobStatus.PLANNING)
    try:
        await pipeline.start_planning(job_id, instructions="do it well")
        with session_scope() as db:
            job = db.get(Job, job_id)
            assert job.status == JobStatus.AWAITING_PLAN_APPROVAL
            assert job.workspace_path
            folder = Path(job.workspace_path)
            assert (folder / "PLAN.md").exists()
            assert (folder / "BRIEF.md").exists()
    finally:
        _delete(job_id)


async def test_start_planning_auto_executes_when_plan_gate_disabled(agent_env, monkeypatch):
    os.environ["AIFOS_AGENT_PLAN_GATE"] = "false"
    get_settings.cache_clear()
    calls: list[tuple[str, str | int | None]] = []

    async def fake_plan(job, folder, settings):
        (folder / "PLAN.md").write_text("# Plan\n1. Implement\n2. Test\n", encoding="utf-8")
        return AgentRun(ok=True, result_text="planned")

    async def fake_execute(job_id, callback_chat_id=None):
        calls.append((job_id, callback_chat_id))

    monkeypatch.setattr(worker_agent, "plan", fake_plan)
    monkeypatch.setattr(pipeline, "execute_approved_plan", fake_execute)

    job_id = _make_job("https://ex.test/agent-autoplan", JobStatus.PLANNING)
    try:
        await pipeline.start_planning(job_id, instructions="run without a manual plan gate", callback_chat_id=123)
        with session_scope() as db:
            job = db.get(Job, job_id)
            assert job.status == JobStatus.IN_PROGRESS
            assert job.workspace_path
        assert calls == [(job_id, 123)]
    finally:
        _delete(job_id)


async def test_execute_approved_plan_completes(agent_env, monkeypatch):
    async def fake_execute(job, folder, settings, previous_review=None):
        (folder / "main.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
        (folder / "SUMMARY.md").write_text("Implemented add().\n", encoding="utf-8")
        return AgentRun(ok=True)

    async def fake_review(job, folder, settings):
        return worker_agent.ReviewResult(
            completion_percent=96, passed=True, summary="Works and tested.", blockers=[], checklist=[], raw={}
        )

    monkeypatch.setattr(worker_agent, "execute", fake_execute)
    monkeypatch.setattr(worker_agent, "review", fake_review)

    job_id = _make_job("https://ex.test/agent-exec", JobStatus.IN_PROGRESS)
    with session_scope() as db:
        job = db.get(Job, job_id)
        folder = create_job_folder(job, get_settings())
        job.workspace_path = str(folder)
    try:
        await pipeline.execute_approved_plan(job_id)
        with session_scope() as db:
            job = db.get(Job, job_id)
            assert job.status == JobStatus.DELIVERY_READY
            assert job.delivery_path
            assert (Path(job.delivery_path) / "qa" / "review.json").exists()
            assert (Path(job.delivery_path) / "qa" / "review_attempt_1.json").exists()
    finally:
        _delete(job_id)


async def test_execute_repairs_then_qa_fails(agent_env, monkeypatch):
    async def fake_execute(job, folder, settings, previous_review=None):
        return AgentRun(ok=True)

    async def fake_review(job, folder, settings):
        return worker_agent.ReviewResult(
            completion_percent=40, passed=False, summary="Incomplete.", blockers=["missing tests"], checklist=[], raw={}
        )

    monkeypatch.setattr(worker_agent, "execute", fake_execute)
    monkeypatch.setattr(worker_agent, "review", fake_review)

    job_id = _make_job("https://ex.test/agent-fail", JobStatus.IN_PROGRESS)
    with session_scope() as db:
        job = db.get(Job, job_id)
        folder = create_job_folder(job, get_settings())
        job.workspace_path = str(folder)
    try:
        await pipeline.execute_approved_plan(job_id)
        with session_scope() as db:
            assert db.get(Job, job_id).status == JobStatus.QA_FAILED
    finally:
        _delete(job_id)


async def test_dispatch_start_routes_to_planning(agent_env, monkeypatch):
    calls: list[str] = []

    async def fake_enqueue(func, *args, background_tasks=None):
        calls.append(func.__name__)

    monkeypatch.setattr(telegram_dispatch, "enqueue", fake_enqueue)

    job_id = _make_job("https://ex.test/agent-start", JobStatus.PROPOSAL_READY)
    try:
        res = await telegram_dispatch.dispatch_callback(
            data=f"start_{job_id}",
            callback_id="",
            callback_chat_id=None,
            callback_message_id=None,
            settings=get_settings(),
            background_tasks=None,
        )
        assert res["status"] == "planning"
        assert "start_planning" in calls
    finally:
        _delete(job_id)


async def test_dispatch_plan_ok_enqueues_execute(agent_env, monkeypatch):
    calls: list[str] = []

    async def fake_enqueue(func, *args, background_tasks=None):
        calls.append(func.__name__)

    monkeypatch.setattr(telegram_dispatch, "enqueue", fake_enqueue)

    job_id = _make_job("https://ex.test/agent-planok", JobStatus.AWAITING_PLAN_APPROVAL)
    try:
        res = await telegram_dispatch.dispatch_callback(
            data=f"plan_ok_{job_id}",
            callback_id="",
            callback_chat_id=None,
            callback_message_id=None,
            settings=get_settings(),
            background_tasks=None,
        )
        assert res["status"] == "in_progress"
        assert "execute_approved_plan" in calls
    finally:
        _delete(job_id)
