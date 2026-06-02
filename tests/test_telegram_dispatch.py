from app.core.config import get_settings
from app.db import session_scope
from app.models import Job, JobStatus
from app.services import telegram_dispatch
from app.services.telegram_dispatch import parse_callback_data


def test_parse_callback_data():
    assert parse_callback_data("approve_abc") == ("approve", "abc")
    assert parse_callback_data("dismiss_xyz") == ("reject", "xyz")
    assert parse_callback_data("start_1") == ("start", "1")
    assert parse_callback_data("accept_7") == ("accept", "7")
    assert parse_callback_data("reject:9") == ("reject", "9")
    assert parse_callback_data("nonsense") == (None, None)


def _make_job(url: str, status: JobStatus) -> str:
    with session_scope() as db:
        job = Job(source="upwork", external_url=url, title="t", description_raw="d", status=status)
        db.add(job)
        db.flush()
        return job.id


def _delete(job_id: str) -> None:
    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is not None:
            db.delete(job)


async def test_dispatch_approve_transitions_and_enqueues(client, monkeypatch):
    calls: list[str] = []

    async def fake_enqueue(func, *args, background_tasks=None):
        calls.append(func.__name__)

    monkeypatch.setattr(telegram_dispatch, "enqueue", fake_enqueue)

    job_id = _make_job("https://ex.test/disp-approve", JobStatus.AWAITING_HUMAN_REVIEW)
    try:
        res = await telegram_dispatch.dispatch_callback(
            data=f"approve_{job_id}",
            callback_id="",
            callback_chat_id=None,
            callback_message_id=None,
            settings=get_settings(),
            background_tasks=None,
        )
        assert res["status"] == "generating_proposal"
        assert "process_approved_job" in calls
        with session_scope() as db:
            assert db.get(Job, job_id).status == JobStatus.GENERATING_PROPOSAL
    finally:
        _delete(job_id)


async def test_dispatch_accept_acknowledges_without_state_change(client, monkeypatch):
    calls: list[str] = []

    async def fake_enqueue(func, *args, background_tasks=None):
        calls.append(func.__name__)

    monkeypatch.setattr(telegram_dispatch, "enqueue", fake_enqueue)

    job_id = _make_job("https://ex.test/disp-accept", JobStatus.DELIVERY_READY)
    try:
        res = await telegram_dispatch.dispatch_callback(
            data=f"accept_{job_id}",
            callback_id="",
            callback_chat_id=None,
            callback_message_id=None,
            settings=get_settings(),
            background_tasks=None,
        )
        assert res["detail"] == "accepted"
        assert calls == []
        with session_scope() as db:
            assert db.get(Job, job_id).status == JobStatus.DELIVERY_READY
    finally:
        _delete(job_id)


async def test_dispatch_rerun_from_qa_failed_enqueues_planning(client, monkeypatch):
    monkeypatch.setenv("AIFOS_WORKER_ENGINE", "claude_code")
    get_settings.cache_clear()
    calls: list[str] = []

    async def fake_enqueue(func, *args, background_tasks=None):
        calls.append(func.__name__)

    monkeypatch.setattr(telegram_dispatch, "enqueue", fake_enqueue)

    job_id = _make_job("https://ex.test/disp-rerun", JobStatus.QA_FAILED)
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
        with session_scope() as db:
            assert db.get(Job, job_id).status == JobStatus.PLANNING
    finally:
        _delete(job_id)
        get_settings.cache_clear()


async def test_dispatch_approve_when_not_pending_is_noop(client, monkeypatch):
    calls: list[str] = []

    async def fake_enqueue(func, *args, background_tasks=None):
        calls.append(func.__name__)

    monkeypatch.setattr(telegram_dispatch, "enqueue", fake_enqueue)

    job_id = _make_job("https://ex.test/disp-already", JobStatus.PROPOSAL_READY)
    try:
        res = await telegram_dispatch.dispatch_callback(
            data=f"approve_{job_id}",
            callback_id="",
            callback_chat_id=None,
            callback_message_id=None,
            settings=get_settings(),
            background_tasks=None,
        )
        assert res["detail"] == "already_processed"
        assert calls == []
    finally:
        _delete(job_id)
