"""
ARQ worker — pipeline task functions with self-healing agent chain.

Each agent job:
  1. Retries itself internally up to MAX_AGENT_RETRIES times (exponential backoff)
  2. On final failure, calls identify_and_rescue() — the supervisor re-enqueues
     the same job so another worker pick-up gets another full retry cycle
  3. Gives up only after SUPERVISOR_RESCUE_LIMIT total rescues per company per agent
"""
import asyncio
import logging
from datetime import datetime, timezone

from arq.connections import RedisSettings
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

MAX_AGENT_RETRIES = 3        # internal retries inside each job execution
RETRY_BASE_DELAY  = 8.0      # seconds — doubles each attempt
RETRY_MAX_DELAY   = 60.0     # cap


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── DB helpers ────────────────────────────────────────────────────────────────

async def _mark_company_failed(company_id: str, reason: str) -> None:
    from app.models.company import Company
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if company:
            company.status = "failed"
            await db.commit()
    logger.error("[WORKER] Company %s marked failed: %s", company_id, reason)


async def _pipeline_failed(pipeline_run_id: str, reason: str) -> None:
    from app.models.pipeline_run import PipelineRun
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
        run = result.scalar_one_or_none()
        if run:
            run.status = "failed"
            run.error_message = reason
            await db.commit()


async def _research_done(company_id: str, agent_names: list[str]) -> bool:
    """Return True if all given agents have a research record for this company."""
    from sqlalchemy import func
    from app.models.research import Research
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count())
            .select_from(Research)
            .where(Research.company_id == company_id)
            .where(Research.agent_name.in_(agent_names))
        )
        count = result.scalar() or 0
    return count >= len(agent_names)


async def _maybe_complete_pipeline(pipeline_run_id: str) -> None:
    from app.models.pipeline_run import PipelineRun
    from app.models.company import Company
    async with AsyncSessionLocal() as db:
        run_result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
        run = run_result.scalar_one_or_none()
        if not run or run.status != "running":
            return
        companies_result = await db.execute(
            select(Company).where(Company.status.in_(["processed", "failed"]))
        )
        done_count = len(companies_result.scalars().all())
        if done_count >= run.total_companies:
            run.status = "completed"
            run.completed_at = _now()
            await db.commit()
            logger.info("[WORKER] Pipeline %s completed (%d companies)", pipeline_run_id, done_count)


# ── generic retry wrapper ─────────────────────────────────────────────────────

async def _run_with_retry(fn, *args, label: str = "agent"):
    """
    Execute an async callable with exponential-backoff retries.
    Raises the last exception after MAX_AGENT_RETRIES attempts.
    """
    delay = RETRY_BASE_DELAY
    last_exc: Exception = RuntimeError("no attempts")
    for attempt in range(1, MAX_AGENT_RETRIES + 1):
        try:
            return await fn(*args)
        except Exception as exc:
            last_exc = exc
            if attempt == MAX_AGENT_RETRIES:
                break
            wait = min(delay, RETRY_MAX_DELAY)
            logger.warning(
                "[%s] attempt %d/%d failed — retrying in %.0fs: %s",
                label.upper(), attempt, MAX_AGENT_RETRIES, wait, exc,
            )
            await asyncio.sleep(wait)
            delay *= 2
    logger.error("[%s] all %d attempts exhausted: %s", label.upper(), MAX_AGENT_RETRIES, last_exc)
    raise last_exc


# ── pipeline orchestrator ─────────────────────────────────────────────────────

async def run_pipeline(ctx, pipeline_run_id: str, filters: dict):
    """Top-level orchestrator: runs Agent 1, then fans out Agents 2+ per company."""
    from app.models.pipeline_run import PipelineRun

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
        run = result.scalar_one_or_none()
        if not run:
            logger.error("[WORKER] Pipeline run %s not found", pipeline_run_id)
            return
        run.status = "running"
        run.current_agent = "agent1_discovery"
        run.started_at = _now()
        await db.commit()

    try:
        from app.agents.agent1_discovery import run_discovery
        companies = await _run_with_retry(
            run_discovery,
            filters["city"],
            filters["sector"],
            filters.get("max_companies", 20),
            pipeline_run_id,
            label="agent1",
        )

        if not companies:
            await _pipeline_failed(pipeline_run_id, "Agent 1 discovered 0 companies.")
            return

        pool = ctx["redis"]
        for company_id in companies:
            await pool.enqueue_job(
                "run_agent2", str(company_id), pipeline_run_id,
                filters.get("resume_text", ""),
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
            run = result.scalar_one_or_none()
            if run:
                run.total_companies = len(companies)
                run.agents_done = ["agent1_discovery"]
                run.current_agent = "agent2_intelligence"
                await db.commit()

        # Schedule supervisor sweep 3 minutes after agent1 completes
        await pool.enqueue_job(
            "run_supervisor_sweep",
            pipeline_run_id,
            filters.get("resume_text", ""),
            _defer_by=180,  # seconds
        )

    except Exception as exc:
        logger.exception("[WORKER] Pipeline %s failed at agent1", pipeline_run_id)
        await _pipeline_failed(pipeline_run_id, str(exc))


# ── per-company agent chain ───────────────────────────────────────────────────

async def run_agent2(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    if await _research_done(company_id, ["agent2_intelligence"]):
        logger.info("[AGENT2] Already done for %s — forwarding", company_id)
        await ctx["redis"].enqueue_job("run_agent3", company_id, pipeline_run_id, resume_text)
        return

    from app.agents.agent2_intelligence import run_intelligence
    try:
        await _run_with_retry(run_intelligence, company_id, label="agent2")
        await ctx["redis"].enqueue_job("run_agent3", company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("[AGENT2] Final failure for company %s", company_id)
        from app.agents.supervisor import identify_and_rescue
        rescued = await identify_and_rescue(
            ctx, "agent2_intelligence", company_id, pipeline_run_id, resume_text
        )
        if not rescued:
            await _mark_company_failed(company_id, f"agent2 unrecoverable: {exc}")


async def run_agent3(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    if await _research_done(company_id, ["agent3_opportunity"]):
        logger.info("[AGENT3] Already done for %s — forwarding", company_id)
        await ctx["redis"].enqueue_job("run_agent4", company_id, pipeline_run_id, resume_text)
        return

    from app.agents.agent3_opportunity import run_opportunity_detection
    try:
        await _run_with_retry(run_opportunity_detection, company_id, label="agent3")
        await ctx["redis"].enqueue_job("run_agent4", company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("[AGENT3] Final failure for company %s", company_id)
        from app.agents.supervisor import identify_and_rescue
        rescued = await identify_and_rescue(
            ctx, "agent3_opportunity", company_id, pipeline_run_id, resume_text
        )
        if not rescued:
            await _mark_company_failed(company_id, f"agent3 unrecoverable: {exc}")


async def run_agent4(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent4_skill_match import run_skill_match
    try:
        top_opp_ids = await _run_with_retry(run_skill_match, company_id, resume_text, label="agent4")
        pool = ctx["redis"]
        for opp_id in top_opp_ids:
            await pool.enqueue_job("run_agent5", str(opp_id), company_id, pipeline_run_id, resume_text)
        await pool.enqueue_job("run_agent6", company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("[AGENT4] Final failure for company %s", company_id)
        from app.agents.supervisor import identify_and_rescue
        rescued = await identify_and_rescue(
            ctx, "agent4_skill_match", company_id, pipeline_run_id, resume_text
        )
        if not rescued:
            await _mark_company_failed(company_id, f"agent4 unrecoverable: {exc}")


async def run_agent5(ctx, opportunity_id: str, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent5_pow import run_pow_generation
    try:
        await _run_with_retry(run_pow_generation, opportunity_id, label="agent5")
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("[AGENT5] Final failure for opportunity %s", opportunity_id)
        from app.agents.supervisor import identify_and_rescue
        await identify_and_rescue(
            ctx, "agent5_pow", company_id, pipeline_run_id, resume_text,
            opportunity_id=opportunity_id,
        )
        # Always attempt agent7 barrier check — agent6 may still complete the chain
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)


async def run_agent6(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    if await _research_done(company_id, ["agent6_founder_research"]):
        logger.info("[AGENT6] Already done for %s — checking barrier", company_id)
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)
        return

    from app.agents.agent6_founder_research import run_founder_research
    try:
        await _run_with_retry(run_founder_research, company_id, label="agent6")
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("[AGENT6] Final failure for company %s", company_id)
        from app.agents.supervisor import identify_and_rescue
        rescued = await identify_and_rescue(
            ctx, "agent6_founder_research", company_id, pipeline_run_id, resume_text
        )
        if not rescued:
            await _mark_company_failed(company_id, f"agent6 unrecoverable: {exc}")


async def _check_and_enqueue_agent7(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    """Barrier: enqueue agent7 only when both agent5 and agent6 have research records."""
    from sqlalchemy import func
    from app.models.research import Research

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count())
            .select_from(Research)
            .where(Research.company_id == company_id)
            .where(Research.agent_name.in_(["agent5_pow", "agent6_founder_research"]))
        )
        count = result.scalar() or 0

    if count >= 2:
        await ctx["redis"].enqueue_job("run_agent7", company_id, pipeline_run_id, resume_text)


async def run_agent7(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    if await _research_done(company_id, ["agent7_narrative"]):
        logger.info("[AGENT7] Already done for %s — forwarding", company_id)
        await ctx["redis"].enqueue_job("run_agent8", company_id, pipeline_run_id)
        return

    from app.agents.agent7_narrative import run_narrative
    try:
        await _run_with_retry(run_narrative, company_id, resume_text, label="agent7")
        await ctx["redis"].enqueue_job("run_agent8", company_id, pipeline_run_id)
    except Exception as exc:
        logger.exception("[AGENT7] Final failure for company %s", company_id)
        from app.agents.supervisor import identify_and_rescue
        rescued = await identify_and_rescue(
            ctx, "agent7_narrative", company_id, pipeline_run_id, resume_text
        )
        if not rescued:
            await _mark_company_failed(company_id, f"agent7 unrecoverable: {exc}")


async def run_agent8(ctx, company_id: str, pipeline_run_id: str):
    from app.agents.agent8_crm_updater import run_crm_update
    try:
        await _run_with_retry(run_crm_update, company_id, label="agent8")
        from app.models.company import Company
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Company).where(Company.id == company_id))
            company = result.scalar_one_or_none()
            if company and company.status != "failed":
                company.status = "processed"
                await db.commit()
        await _maybe_complete_pipeline(pipeline_run_id)
    except Exception as exc:
        logger.exception("[AGENT8] Final failure for company %s", company_id)
        from app.agents.supervisor import identify_and_rescue
        rescued = await identify_and_rescue(
            ctx, "agent8_crm_updater", company_id, pipeline_run_id
        )
        if not rescued:
            await _mark_company_failed(company_id, f"agent8 unrecoverable: {exc}")


# ── supervisor sweep (periodic health check) ──────────────────────────────────

async def run_supervisor_sweep(ctx, pipeline_run_id: str, resume_text: str = ""):
    """
    Scheduled sweep: find companies stuck in 'processing' and rescue them.
    Enqueue this job once per pipeline run after agent1 completes.
    """
    from app.agents.supervisor import scan_stuck_companies
    rescued = await scan_stuck_companies(ctx, pipeline_run_id, resume_text)
    logger.info("[SUPERVISOR] Sweep complete — rescued %d companies", rescued)


# ── worker settings ───────────────────────────────────────────────────────────

async def startup(ctx):
    logger.info("[WORKER] ARQ worker started — DeepSeek model: %s", settings.deepseek_model)


async def shutdown(ctx):
    logger.info("[WORKER] ARQ worker shutting down")


class WorkerSettings:
    functions = [
        run_pipeline,
        run_agent2,
        run_agent3,
        run_agent4,
        run_agent5,
        run_agent6,
        run_agent7,
        run_agent8,
        run_supervisor_sweep,
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 10
    job_timeout = 600
    retry_jobs = False   # Self-healing is handled inside each job — ARQ retries disabled
