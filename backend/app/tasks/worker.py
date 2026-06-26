"""ARQ worker — all pipeline task functions live here."""
import logging
from datetime import datetime, timezone

from arq.connections import RedisSettings
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# ── helpers ──────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _mark_company_failed(company_id: str, reason: str) -> None:
    """Set company.status = 'failed' so the UI can surface the error state."""
    from app.models.company import Company

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if company:
            company.status = "failed"
            await db.commit()
    logger.error("Company %s marked failed: %s", company_id, reason)


async def _pipeline_failed(pipeline_run_id: str, reason: str) -> None:
    """Set pipeline_run.status = 'failed' with an error message."""
    from app.models.pipeline_run import PipelineRun

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
        run = result.scalar_one_or_none()
        if run:
            run.status = "failed"
            run.error_message = reason
            await db.commit()


async def _research_done(company_id: str, agent_names: list[str]) -> bool:
    """Return True if all given agent_names have a research record for this company (dedup guard)."""
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


# ── pipeline orchestrator ─────────────────────────────────────────────────────

async def run_pipeline(ctx, pipeline_run_id: str, filters: dict):
    """Top-level orchestrator: runs Agent 1, then fans out Agents 2+ per company."""
    from app.models.pipeline_run import PipelineRun

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
        run = result.scalar_one_or_none()
        if not run:
            logger.error("Pipeline run %s not found", pipeline_run_id)
            return

        run.status = "running"
        run.current_agent = "agent1_discovery"
        run.started_at = _now()
        await db.commit()

    try:
        from app.agents.agent1_discovery import run_discovery
        companies = await run_discovery(
            city=filters["city"],
            sector=filters["sector"],
            max_companies=filters.get("max_companies", 20),
            pipeline_run_id=pipeline_run_id,
        )

        if not companies:
            await _pipeline_failed(pipeline_run_id, "Agent 1 discovered 0 companies — check city/sector filters.")
            return

        pool = ctx["redis"]
        for company_id in companies:
            await pool.enqueue_job("run_agent2", str(company_id), pipeline_run_id, filters.get("resume_text", ""))

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
            run = result.scalar_one_or_none()
            if run:
                run.total_companies = len(companies)
                run.agents_done = ["agent1_discovery"]
                run.current_agent = "agent2_intelligence"
                await db.commit()

    except Exception as exc:
        logger.exception("Pipeline %s failed at agent1", pipeline_run_id)
        await _pipeline_failed(pipeline_run_id, str(exc))


# ── per-company agent chain ───────────────────────────────────────────────────

async def run_agent2(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    # Dedup: skip if agent2 already ran successfully for this company
    if await _research_done(company_id, ["agent2_intelligence"]):
        logger.info("Agent2 already done for company %s; skipping", company_id)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent3", company_id, pipeline_run_id, resume_text)
        return

    from app.agents.agent2_intelligence import run_intelligence
    try:
        await run_intelligence(company_id)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent3", company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("Agent2 failed for company %s", company_id)
        await _mark_company_failed(company_id, f"agent2: {exc}")


async def run_agent3(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    if await _research_done(company_id, ["agent3_opportunity"]):
        logger.info("Agent3 already done for company %s; skipping", company_id)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent4", company_id, pipeline_run_id, resume_text)
        return

    from app.agents.agent3_opportunity import run_opportunity_detection
    try:
        await run_opportunity_detection(company_id)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent4", company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("Agent3 failed for company %s", company_id)
        await _mark_company_failed(company_id, f"agent3: {exc}")


async def run_agent4(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent4_skill_match import run_skill_match
    try:
        top_opp_ids = await run_skill_match(company_id, resume_text)
        pool = ctx["redis"]
        for opp_id in top_opp_ids:
            await pool.enqueue_job("run_agent5", str(opp_id), company_id, pipeline_run_id, resume_text)
        await pool.enqueue_job("run_agent6", company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("Agent4 failed for company %s", company_id)
        await _mark_company_failed(company_id, f"agent4: {exc}")


async def run_agent5(ctx, opportunity_id: str, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent5_pow import run_pow_generation
    try:
        await run_pow_generation(opportunity_id)
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("Agent5 failed for opportunity %s", opportunity_id)
        # Don't mark whole company failed — still try agent7 via agent6 barrier
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)


async def run_agent6(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    if await _research_done(company_id, ["agent6_founder_research"]):
        logger.info("Agent6 already done for company %s; skipping", company_id)
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)
        return

    from app.agents.agent6_founder_research import run_founder_research
    try:
        await run_founder_research(company_id)
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)
    except Exception as exc:
        logger.exception("Agent6 failed for company %s", company_id)
        await _mark_company_failed(company_id, f"agent6: {exc}")


async def _check_and_enqueue_agent7(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    """Barrier: only enqueue agent7 when both agent5 and agent6 have completed."""
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
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent7", company_id, pipeline_run_id, resume_text)


async def run_agent7(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    if await _research_done(company_id, ["agent7_narrative"]):
        logger.info("Agent7 already done for company %s; skipping", company_id)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent8", company_id, pipeline_run_id)
        return

    from app.agents.agent7_narrative import run_narrative
    try:
        await run_narrative(company_id, resume_text)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent8", company_id, pipeline_run_id)
    except Exception as exc:
        logger.exception("Agent7 failed for company %s", company_id)
        await _mark_company_failed(company_id, f"agent7: {exc}")


async def run_agent8(ctx, company_id: str, pipeline_run_id: str):
    from app.agents.agent8_crm_updater import run_crm_update
    try:
        await run_crm_update(company_id)
        # Mark company as fully processed
        from app.models.company import Company
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Company).where(Company.id == company_id))
            company = result.scalar_one_or_none()
            if company and company.status != "failed":
                company.status = "processed"
                await db.commit()

        # Check if all companies in this pipeline are done
        await _maybe_complete_pipeline(pipeline_run_id)
    except Exception as exc:
        logger.exception("Agent8 failed for company %s", company_id)
        await _mark_company_failed(company_id, f"agent8: {exc}")


async def _maybe_complete_pipeline(pipeline_run_id: str) -> None:
    """Mark the pipeline as completed when every company is processed or failed."""
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
            logger.info("Pipeline %s completed (%d companies)", pipeline_run_id, done_count)


# ── worker settings ───────────────────────────────────────────────────────────

async def startup(ctx):
    logger.info("ARQ worker started")


async def shutdown(ctx):
    logger.info("ARQ worker shutting down")


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
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 10
    job_timeout = 600  # increased to 10 min to accommodate retries inside agents
    retry_jobs = True
    max_tries = 1  # ARQ-level retries disabled — each agent handles its own retries
