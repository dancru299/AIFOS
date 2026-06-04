from app.models import Job, JobEvent, JobStatus

ALLOWED_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.PENDING: {JobStatus.ANALYZING},
    JobStatus.ANALYZING: {JobStatus.DISCARDED, JobStatus.AWAITING_HUMAN_REVIEW, JobStatus.ANALYSIS_FAILED},
    JobStatus.DISCARDED: set(),
    JobStatus.AWAITING_HUMAN_REVIEW: {JobStatus.GENERATING_PROPOSAL, JobStatus.REJECTED},
    JobStatus.GENERATING_PROPOSAL: {JobStatus.PROPOSAL_READY, JobStatus.PROPOSAL_FAILED},
    JobStatus.PROPOSAL_READY: {JobStatus.IN_PROGRESS, JobStatus.PLANNING},
    JobStatus.PLANNING: {JobStatus.AWAITING_PLAN_APPROVAL, JobStatus.IN_PROGRESS, JobStatus.WORK_FAILED},
    JobStatus.AWAITING_PLAN_APPROVAL: {JobStatus.IN_PROGRESS, JobStatus.PROPOSAL_READY},
    JobStatus.IN_PROGRESS: {JobStatus.QA_RUNNING, JobStatus.WORK_FAILED},
    JobStatus.QA_RUNNING: {JobStatus.IN_PROGRESS, JobStatus.DELIVERY_READY, JobStatus.QA_FAILED},
    JobStatus.DELIVERY_READY: {JobStatus.IN_PROGRESS, JobStatus.PLANNING},
    JobStatus.WORK_FAILED: {JobStatus.IN_PROGRESS, JobStatus.PLANNING},
    JobStatus.QA_FAILED: {JobStatus.IN_PROGRESS, JobStatus.PLANNING},
    JobStatus.REJECTED: set(),
    JobStatus.ANALYSIS_FAILED: {JobStatus.ANALYZING},
    JobStatus.PROPOSAL_FAILED: {JobStatus.GENERATING_PROPOSAL},
}


def transition_job(job: Job, next_status: JobStatus, detail: str | None = None) -> None:
    if job.status == next_status:
        return

    allowed = ALLOWED_TRANSITIONS.get(job.status, set())
    if next_status not in allowed:
        raise ValueError(f"Invalid job status transition: {job.status.value} -> {next_status.value}")

    # Record the transition on the timeline. Appending to the relationship lets
    # the surrounding session_scope persist it on commit (job is always attached).
    job.events.append(JobEvent(from_status=job.status.value, to_status=next_status.value, detail=detail))
    job.status = next_status
