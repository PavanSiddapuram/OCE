"""ARQ worker — all pipeline task functions live here."""
import logging
from datetime import datetime

from arq.connections import RedisSettings

from app.config import settings
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def run_pipeline(ctx, pipeline_run_id: str, filters: dict):
    """Top-level orchestrator: runs Agent 1, then fans out Agents 2+ per company."""
    from sqlalchemy import select
    from app.models.pipeline_run import PipelineRun

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
        run = result.scalar_one_or_none()
        if not run:
            logger.error(f"Pipeline run {pipeline_run_id} not found")
            return

        run.status = "running"
        run.current_agent = "agent1_discovery"
        run.started_at = datetime.utcnow()
        await db.commit()

    try:
        from app.agents.agent1_discovery import run_discovery
        companies = await run_discovery(
            city=filters["city"],
            sector=filters["sector"],
            max_companies=filters.get("max_companies", 20),
            pipeline_run_id=pipeline_run_id,
        )

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

    except Exception as e:
        logger.exception(f"Pipeline {pipeline_run_id} failed at agent1: {e}")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(PipelineRun).where(PipelineRun.id == pipeline_run_id))
            run = result.scalar_one_or_none()
            if run:
                run.status = "failed"
                run.error_message = str(e)
                await db.commit()


async def run_agent2(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent2_intelligence import run_intelligence
    try:
        await run_intelligence(company_id)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent3", company_id, pipeline_run_id, resume_text)
    except Exception as e:
        logger.exception(f"Agent2 failed for company {company_id}: {e}")


async def run_agent3(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent3_opportunity import run_opportunity_detection
    try:
        await run_opportunity_detection(company_id)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent4", company_id, pipeline_run_id, resume_text)
    except Exception as e:
        logger.exception(f"Agent3 failed for company {company_id}: {e}")


async def run_agent4(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent4_skill_match import run_skill_match
    try:
        top_opp_ids = await run_skill_match(company_id, resume_text)
        pool = ctx["redis"]
        for opp_id in top_opp_ids:
            await pool.enqueue_job("run_agent5", str(opp_id), company_id, pipeline_run_id, resume_text)
        await pool.enqueue_job("run_agent6", company_id, pipeline_run_id, resume_text)
    except Exception as e:
        logger.exception(f"Agent4 failed for company {company_id}: {e}")


async def run_agent5(ctx, opportunity_id: str, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent5_pow import run_pow_generation
    try:
        await run_pow_generation(opportunity_id)
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)
    except Exception as e:
        logger.exception(f"Agent5 failed for opportunity {opportunity_id}: {e}")


async def run_agent6(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent6_founder_research import run_founder_research
    try:
        await run_founder_research(company_id)
        await _check_and_enqueue_agent7(ctx, company_id, pipeline_run_id, resume_text)
    except Exception as e:
        logger.exception(f"Agent6 failed for company {company_id}: {e}")


async def _check_and_enqueue_agent7(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    """Barrier: only enqueue agent7 when both agent5 and agent6 have completed for this company."""
    from sqlalchemy import select, func
    from app.models.research import Research

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count())
            .where(Research.company_id == company_id)
            .where(Research.agent_name.in_(["agent5_pow", "agent6_founder_research"]))
        )
        count = result.scalar()

    if count and count >= 2:
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent7", company_id, pipeline_run_id, resume_text)


async def run_agent7(ctx, company_id: str, pipeline_run_id: str, resume_text: str):
    from app.agents.agent7_narrative import run_narrative
    try:
        await run_narrative(company_id, resume_text)
        pool = ctx["redis"]
        await pool.enqueue_job("run_agent8", company_id, pipeline_run_id)
    except Exception as e:
        logger.exception(f"Agent7 failed for company {company_id}: {e}")


async def run_agent8(ctx, company_id: str, pipeline_run_id: str):
    from app.agents.agent8_crm_updater import run_crm_update
    try:
        await run_crm_update(company_id)
    except Exception as e:
        logger.exception(f"Agent8 failed for company {company_id}: {e}")


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
    job_timeout = 300
