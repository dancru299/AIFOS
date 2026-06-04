import json
import logging
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import get_settings
from app.db import session_scope
from app.models import Job, JobStatus, ProjectTask, QAStatus, TaskScope
from app.services.agent import worker_agent
from app.services.agent.job_folder import create_job_folder, read_text_if_exists, write_brief
from app.services.analyst import AnalystService
from app.services.delivery import DeliveryService
from app.services.portfolio import PortfolioService
from app.services.proposal import ProposalService
from app.services.qa import GateResult, QAService, run_quality_gate
from app.services.telegram import TelegramService
from app.services.workers import WorkerContext, get_worker_for_scope
from app.services.workspace import WorkspaceService
from app.state_machine import transition_job

logger = logging.getLogger(__name__)


async def analyze_job(job_id: str) -> None:
    settings = get_settings()
    analyst_service = AnalystService(settings)
    telegram_service = TelegramService(settings)

    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None:
            logger.warning("Job %s not found for analysis", job_id)
            return
        if job.status == JobStatus.PENDING:
            transition_job(job, JobStatus.ANALYZING)

    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None:
            return
        try:
            decision = await analyst_service.analyze_job(job)
            job.roi_score = decision.score
            job.is_good_job = decision.is_good_job
            job.budget_estimate = decision.budget_estimate
            job.tech_stack = decision.tech_stack
            job.client_country = decision.client_country
            job.analysis_reasoning = decision.reasoning
            job.last_error = None
            if decision.score >= settings.analyst_threshold or decision.is_good_job:
                transition_job(job, JobStatus.AWAITING_HUMAN_REVIEW)
            else:
                transition_job(job, JobStatus.DISCARDED)
        except Exception as exc:
            job.last_error = str(exc)
            transition_job(job, JobStatus.ANALYSIS_FAILED)
            logger.exception("Analysis failed for job %s", job_id)
            return

    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None or job.status != JobStatus.AWAITING_HUMAN_REVIEW:
            return
        message_ref = await telegram_service.send_job_alert(job)
        if message_ref:
            job.telegram_chat_id = message_ref.chat_id
            job.telegram_alert_message_id = message_ref.message_id


async def process_approved_job(job_id: str, callback_query_id: str | None, callback_chat_id: str | int | None, callback_message_id: int | None) -> None:
    settings = get_settings()
    portfolio_service = PortfolioService(settings)
    proposal_service = ProposalService(settings)
    telegram_service = TelegramService(settings)

    if callback_query_id:
        await telegram_service.answer_callback_query(callback_query_id, "Generating proposal...")
    await telegram_service.clear_inline_keyboard(callback_chat_id, callback_message_id)

    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None:
            logger.warning("Job %s not found for approval pipeline", job_id)
            return

    await telegram_service.send_generation_started(job, callback_chat_id)

    try:
        portfolio_markdown = portfolio_service.load_markdown()
    except Exception as exc:
        failed_job = None
        with session_scope() as db:
            job = db.get(Job, job_id)
            if job:
                job.last_error = str(exc)
                transition_job(job, JobStatus.PROPOSAL_FAILED)
                failed_job = job
        if failed_job:
            await telegram_service.send_proposal_failed(failed_job, callback_chat_id)
        logger.exception("Portfolio loading failed for job %s", job_id)
        return

    try:
        proposal = await proposal_service.generate_proposal(job, portfolio_markdown)
    except Exception as exc:
        failed_job = None
        with session_scope() as db:
            job = db.get(Job, job_id)
            if job:
                job.last_error = str(exc)
                transition_job(job, JobStatus.PROPOSAL_FAILED)
                failed_job = job
        if failed_job:
            await telegram_service.send_proposal_failed(failed_job, callback_chat_id)
        logger.exception("Proposal generation failed for job %s", job_id)
        return

    ready_job = None
    with session_scope() as db:
        job = db.get(Job, job_id)
        if job:
            job.proposal_text = proposal.proposal_text
            job.proposal_price = proposal.estimated_bid
            job.proposal_timeline = proposal.timeline
            job.proposal_generated_at = datetime.now(UTC)
            job.last_error = None
            transition_job(job, JobStatus.PROPOSAL_READY)
            ready_job = job

    if ready_job:
        await telegram_service.send_proposal(ready_job, callback_chat_id)


async def process_rejected_job(job_id: str, callback_query_id: str | None, callback_chat_id: str | int | None, callback_message_id: int | None) -> None:
    settings = get_settings()
    telegram_service = TelegramService(settings)

    if callback_query_id:
        await telegram_service.answer_callback_query(callback_query_id, "Job dismissed.")
    await telegram_service.clear_inline_keyboard(callback_chat_id, callback_message_id)


async def process_started_work(
    job_id: str,
    task_scope: TaskScope | None = None,
    task_title: str | None = None,
    instructions: str | None = None,
    callback_chat_id: str | int | None = None,
) -> None:
    settings = get_settings()
    workspace_service = WorkspaceService(settings)
    qa_service = QAService()
    delivery_service = DeliveryService()
    telegram_service = TelegramService(settings)

    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None:
            logger.warning("Job %s not found for work pipeline", job_id)
            return
        scope = task_scope or _infer_task_scope(job)
        workspace = workspace_service.create_for_job(job)
        workspace_service.write_pm_brief(job, workspace, scope, instructions)
        job.workspace_path = str(workspace.root)
        job.delivery_path = None

        task = ProjectTask(
            job_id=job.id,
            task_title=task_title or _default_task_title(job, scope),
            task_scope=scope,
            qa_status=QAStatus.UNREVIEWED,
        )
        db.add(task)
        db.flush()
        task_id = task.id

    await telegram_service.send_work_started(job, scope, callback_chat_id)

    previous_qa_report: dict | None = None
    max_attempts = max(0, settings.worker_max_repair_attempts) + 1
    for attempt in range(1, max_attempts + 1):
        try:
            with session_scope() as db:
                job = db.get(Job, job_id)
                task = db.get(ProjectTask, task_id)
                if job is None or task is None:
                    return

            worker = get_worker_for_scope(scope, settings)
            result = await worker.generate(
                WorkerContext(
                    job=job,
                    task=task,
                    workspace=workspace,
                    attempt=attempt,
                    previous_qa_report=previous_qa_report,
                    instructions=instructions,
                )
            )
            written_files = worker.write_files(workspace.src, result)

            with session_scope() as db:
                job = db.get(Job, job_id)
                task = db.get(ProjectTask, task_id)
                if job is None or task is None:
                    return
                task.generated_output = json.dumps(
                    {
                        "summary": result.summary,
                        "files": [str(path.relative_to(workspace.root)) for path in written_files],
                        "attempt": attempt,
                    },
                    indent=2,
                )
                task.qa_status = QAStatus.UNREVIEWED
                if job.status == JobStatus.IN_PROGRESS:
                    transition_job(job, JobStatus.QA_RUNNING)
        except Exception as exc:
            failed_job = None
            with session_scope() as db:
                job = db.get(Job, job_id)
                if job:
                    job.last_error = str(exc)
                    if job.status == JobStatus.IN_PROGRESS:
                        transition_job(job, JobStatus.WORK_FAILED)
                    failed_job = job
            if failed_job:
                await telegram_service.send_work_failed(failed_job, f"Worker failed: {exc}", callback_chat_id)
            logger.exception("Worker failed for job %s", job_id)
            return

        qa_result = qa_service.run(scope, workspace, attempt)
        if qa_result.passed:
            delivery_path = delivery_service.create_zip(workspace)
            ready_job = None
            ready_task = None
            with session_scope() as db:
                job = db.get(Job, job_id)
                task = db.get(ProjectTask, task_id)
                if job is None or task is None:
                    return
                task.qa_status = QAStatus.PASSED
                task.qa_logs = json.dumps(qa_result.report, indent=2, ensure_ascii=False)
                job.delivery_path = str(delivery_path)
                job.last_error = None
                transition_job(job, JobStatus.DELIVERY_READY)
                ready_job = job
                ready_task = task
            await telegram_service.send_delivery_ready(ready_job, ready_task, callback_chat_id)
            return

        previous_qa_report = qa_result.report
        should_retry = attempt < max_attempts
        failed_job = None
        with session_scope() as db:
            job = db.get(Job, job_id)
            task = db.get(ProjectTask, task_id)
            if job is None or task is None:
                return
            task.qa_status = QAStatus.FAILED
            task.qa_logs = json.dumps(qa_result.report, indent=2, ensure_ascii=False)
            job.last_error = qa_result.summary
            if should_retry:
                transition_job(job, JobStatus.IN_PROGRESS)
            else:
                transition_job(job, JobStatus.QA_FAILED)
                failed_job = job
        if failed_job:
            await telegram_service.send_work_failed(failed_job, qa_result.summary, callback_chat_id)


def _infer_task_scope(job: Job) -> TaskScope:
    haystack = f"{job.title} {job.description_raw} {' '.join(job.tech_stack or [])}".lower()
    if any(token in haystack for token in ("scrap", "crawl", "crawler", "data extraction", "automation")):
        return TaskScope.SCRAPING
    if any(token in haystack for token in ("blog", "article", "seo", "copywriting", "content", "write")):
        return TaskScope.WRITING
    return TaskScope.CODE


def _default_task_title(job: Job, task_scope: TaskScope) -> str:
    prefix = {
        TaskScope.CODE: "Web/code delivery",
        TaskScope.WRITING: "SEO content delivery",
        TaskScope.SCRAPING: "Scraping delivery",
    }[task_scope]
    return f"{prefix}: {job.title[:120]}"


# --- Agentic (Claude Code) worker engine ---------------------------------------


async def start_planning(job_id: str, instructions: str | None = None, callback_chat_id: str | int | None = None) -> None:
    """Phase 1 of the agentic engine: seed the job folder and let Claude Code draft PLAN.md."""
    settings = get_settings()
    telegram_service = TelegramService(settings)

    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None:
            logger.warning("Job %s not found for planning", job_id)
            return
        folder = create_job_folder(job, settings)
        write_brief(job, folder, instructions)
        job.workspace_path = str(folder)
        job.delivery_path = None

    run = await worker_agent.plan(job, folder, settings)
    _accumulate_cost(job_id, run.cost_usd)
    plan_path = folder / "PLAN.md"

    if not run.ok or not plan_path.exists():
        failed_job = None
        with session_scope() as db:
            job = db.get(Job, job_id)
            if job:
                job.last_error = run.error or "Planner did not produce PLAN.md"
                if job.status == JobStatus.PLANNING:
                    transition_job(job, JobStatus.WORK_FAILED)
                failed_job = job
        if failed_job:
            await telegram_service.send_work_failed(failed_job, failed_job.last_error or "planning failed", callback_chat_id)
        logger.warning("Planning failed for job %s: %s", job_id, run.error)
        return

    plan_text = read_text_if_exists(plan_path, limit=3000)
    if settings.agent_plan_gate:
        ready_job = None
        with session_scope() as db:
            job = db.get(Job, job_id)
            if job and job.status == JobStatus.PLANNING:
                transition_job(job, JobStatus.AWAITING_PLAN_APPROVAL)
                job.last_error = None
                ready_job = job
        if ready_job:
            await telegram_service.send_plan_ready(ready_job, plan_text, callback_chat_id)
        return

    execute_now = False
    with session_scope() as db:
        job = db.get(Job, job_id)
        if job and job.status == JobStatus.PLANNING:
            transition_job(job, JobStatus.IN_PROGRESS)
            job.last_error = None
            execute_now = True
    if execute_now:
        logger.info("Plan gate disabled; executing approved plan immediately for job %s", job_id)
        await execute_approved_plan(job_id, callback_chat_id)


async def execute_approved_plan(job_id: str, callback_chat_id: str | int | None = None) -> None:
    """Phase 2 of the agentic engine: execute the approved plan, then QA-review it."""
    settings = get_settings()
    telegram_service = TelegramService(settings)

    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None:
            return
        folder = Path(job.workspace_path) if job.workspace_path else None

    if folder is None or not folder.exists():
        failed_job = None
        with session_scope() as db:
            job = db.get(Job, job_id)
            if job:
                job.last_error = "Job folder is missing; re-run Start Work."
                if job.status == JobStatus.IN_PROGRESS:
                    transition_job(job, JobStatus.WORK_FAILED)
                failed_job = job
        if failed_job:
            await telegram_service.send_work_failed(failed_job, failed_job.last_error or "missing folder", callback_chat_id)
        return

    await telegram_service.send_work_started(job, _infer_task_scope(job), callback_chat_id)

    previous_review: worker_agent.ReviewResult | None = None
    max_attempts = max(0, settings.agent_max_repairs) + 1

    for attempt in range(1, max_attempts + 1):
        with session_scope() as db:
            job = db.get(Job, job_id)
            if job is None:
                return

        run = await worker_agent.execute(job, folder, settings, previous_review)
        _accumulate_cost(job_id, run.cost_usd)
        if not run.ok:
            failed_job = None
            with session_scope() as db:
                job = db.get(Job, job_id)
                if job:
                    job.last_error = run.error or "Executor run failed"
                    if job.status == JobStatus.IN_PROGRESS:
                        transition_job(job, JobStatus.WORK_FAILED)
                    failed_job = job
            if failed_job:
                await telegram_service.send_work_failed(failed_job, failed_job.last_error or "executor failed", callback_chat_id)
            return

        with session_scope() as db:
            job = db.get(Job, job_id)
            if job and job.status == JobStatus.IN_PROGRESS:
                transition_job(job, JobStatus.QA_RUNNING)

        review_result = await worker_agent.review(job, folder, settings)
        _accumulate_cost(job_id, review_result.cost_usd)
        _write_review_report(folder, review_result, attempt)

        # Deterministic gate: real compile/build with exit codes checked. Delivery
        # requires BOTH the LLM reviewer and this gate to pass, so the agent can't
        # ship code that doesn't build just because it graded itself highly.
        gate: GateResult | None = None
        if settings.agent_quality_gate:
            gate = run_quality_gate(folder, timeout=settings.agent_quality_gate_timeout_seconds)
            _write_gate_report(folder, gate, attempt)

        verdict = review_result
        if gate is not None and not gate.passed:
            blockers = list(review_result.blockers) + [f"[QA gate] {failure}" for failure in gate.failures]
            summary = review_result.summary
            if review_result.passed:
                summary = "Reviewer approved, but the QA gate found build/compile errors."
            verdict = replace(review_result, passed=False, blockers=blockers, summary=summary)

        # Surface anything the agent explicitly flagged for the human.
        questions = read_text_if_exists(folder / "QUESTIONS.md", limit=1500)

        if verdict.passed:
            ready_job = None
            with session_scope() as db:
                job = db.get(Job, job_id)
                if job:
                    job.delivery_path = str(folder)
                    job.last_error = None
                    if job.status == JobStatus.QA_RUNNING:
                        transition_job(job, JobStatus.DELIVERY_READY)
                    ready_job = job
            if ready_job:
                await telegram_service.send_review_ready(ready_job, verdict, callback_chat_id, questions=questions)
            return

        previous_review = verdict
        should_retry = attempt < max_attempts
        final_job = None
        with session_scope() as db:
            job = db.get(Job, job_id)
            if job:
                job.last_error = f"{verdict.completion_percent}% complete: {verdict.summary}"
                if job.status == JobStatus.QA_RUNNING:
                    transition_job(job, JobStatus.IN_PROGRESS if should_retry else JobStatus.QA_FAILED)
                if not should_retry:
                    final_job = job
        if final_job:
            await telegram_service.send_review_ready(final_job, verdict, callback_chat_id, questions=questions)
            return


def _accumulate_cost(job_id: str, cost: float | None) -> None:
    """Add one agent run's USD cost to the job's running total."""
    if not cost:
        return
    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is not None:
            job.total_cost_usd = (job.total_cost_usd or 0.0) + float(cost)


def _write_gate_report(folder: Path, gate: GateResult, attempt: int) -> None:
    qa_dir = folder / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    report = {"attempt": attempt, **gate.to_dict()}
    report_text = json.dumps(report, indent=2, ensure_ascii=False)
    (qa_dir / f"gate_attempt_{attempt}.json").write_text(report_text, encoding="utf-8")
    (qa_dir / "gate.json").write_text(report_text, encoding="utf-8")


def _write_review_report(folder: Path, review_result: "worker_agent.ReviewResult", attempt: int) -> None:
    qa_dir = folder / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "attempt": attempt,
        "completion_percent": review_result.completion_percent,
        "passed": review_result.passed,
        "summary": review_result.summary,
        "blockers": review_result.blockers,
        "checklist": review_result.checklist,
    }
    report_text = json.dumps(report, indent=2, ensure_ascii=False)
    (qa_dir / f"review_attempt_{attempt}.json").write_text(report_text, encoding="utf-8")
    (qa_dir / "review.json").write_text(report_text, encoding="utf-8")
