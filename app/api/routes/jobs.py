from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Job, JobStatus
from app.schemas import JobIngestRequest, JobIngestResponse, JobRead, JobStartWorkRequest, JobStartWorkResponse
from app.services.pipeline import analyze_job, process_started_work
from app.services.tasks import enqueue
from app.state_machine import transition_job

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("/ingest", response_model=JobIngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_job(payload: JobIngestRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> JobIngestResponse:
    existing_job = db.scalar(select(Job).where(Job.external_url == payload.external_url))
    if existing_job:
        return JobIngestResponse(job_id=existing_job.id, status=existing_job.status)

    job = Job(
        source=payload.source,
        external_url=payload.external_url,
        title=payload.title,
        description_raw=payload.description_raw,
        budget_raw=payload.budget_raw,
        client_location=payload.client_location,
        client_metadata=payload.client_metadata,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    await enqueue(analyze_job, job.id, background_tasks=background_tasks)
    return JobIngestResponse(job_id=job.id, status=job.status)


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    jobs = db.scalars(select(Job).order_by(Job.created_at.desc())).all()
    return list(jobs)


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: str, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.post("/{job_id}/start-work", response_model=JobStartWorkResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_work(
    job_id: str,
    background_tasks: BackgroundTasks,
    payload: JobStartWorkRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> JobStartWorkResponse:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.status not in {JobStatus.PROPOSAL_READY, JobStatus.QA_FAILED, JobStatus.WORK_FAILED, JobStatus.DELIVERY_READY}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job cannot start work from status {job.status.value}.",
        )

    payload = payload or JobStartWorkRequest()
    transition_job(job, JobStatus.IN_PROGRESS)
    job.last_error = None
    db.commit()
    db.refresh(job)

    await enqueue(
        process_started_work,
        job.id,
        payload.task_scope,
        payload.task_title,
        payload.instructions,
        None,
        background_tasks=background_tasks,
    )
    return JobStartWorkResponse(job_id=job.id, status=job.status, workspace_path=job.workspace_path)
