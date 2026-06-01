from app.db import session_scope
from app.models import Job, JobStatus
from app.services import recovery


def _make_job(url: str, status: JobStatus) -> str:
    with session_scope() as db:
        job = Job(
            source="upwork",
            external_url=url,
            title="Recovery test job",
            description_raw="desc",
            status=status,
        )
        db.add(job)
        db.flush()
        return job.id


async def test_recover_stuck_jobs(client, monkeypatch):
    calls: list[tuple[str, tuple]] = []

    async def fake_enqueue(func, *args, background_tasks=None):
        calls.append((func.__name__, args))

    monkeypatch.setattr(recovery, "enqueue", fake_enqueue)

    analyzing = _make_job("https://ex.test/rec-analyzing", JobStatus.ANALYZING)
    generating = _make_job("https://ex.test/rec-generating", JobStatus.GENERATING_PROPOSAL)
    in_progress = _make_job("https://ex.test/rec-inprogress", JobStatus.IN_PROGRESS)
    qa_running = _make_job("https://ex.test/rec-qa", JobStatus.QA_RUNNING)

    recovered = await recovery.recover_stuck_jobs()

    assert {analyzing, generating, in_progress, qa_running}.issubset(set(recovered))

    with session_scope() as db:
        assert db.get(Job, analyzing).status == JobStatus.PENDING
        assert db.get(Job, generating).status == JobStatus.GENERATING_PROPOSAL
        assert db.get(Job, in_progress).status == JobStatus.WORK_FAILED
        assert db.get(Job, qa_running).status == JobStatus.WORK_FAILED
        assert db.get(Job, in_progress).last_error == "recovered_after_restart"

    enqueued = [name for name, _ in calls]
    assert "analyze_job" in enqueued
    assert "process_approved_job" in enqueued

    # Clean up so a later app's startup recovery doesn't re-pick these jobs.
    with session_scope() as db:
        for job_id in (analyzing, generating, in_progress, qa_running):
            job = db.get(Job, job_id)
            if job is not None:
                db.delete(job)
