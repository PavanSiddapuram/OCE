"""
Agent Supervisor — Logic Analyser & Self-Healing Coordinator.

Responsibilities:
  1. Detect agents that have been stuck / failed for a company
  2. Re-enqueue the failed agent job so the chain can resume
  3. Record a supervision event in the research table for full audit trail
  4. Expose identify_and_rescue() so any agent can call it on peer failure
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func

from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Ordered chain: each entry is (agent_name_in_research_table, arq_job_name)
AGENT_CHAIN: list[tuple[str, str]] = [
    ("agent2_intelligence",     "run_agent2"),
    ("agent3_opportunity",      "run_agent3"),
    ("agent4_skill_match",      "run_agent4"),
    ("agent5_pow",              "run_agent5"),
    ("agent6_founder_research", "run_agent6"),
    ("agent7_narrative",        "run_agent7"),
    ("agent8_crm_updater",      "run_agent8"),
]

# How long (seconds) before we consider an agent stuck and eligible for rescue
STUCK_THRESHOLD_SECONDS = 120


async def _log_supervision_event(
    company_id: str,
    failed_agent: str,
    action: str,
) -> None:
    """Write a supervision record so the dashboard can show rescue events."""
    from app.models.research import Research

    async with AsyncSessionLocal() as db:
        entry = Research(
            id=uuid.uuid4(),
            company_id=company_id,
            agent_name="supervisor",
            raw_input={"failed_agent": failed_agent},
            raw_output={"action": action},
            model_used="supervisor",
        )
        db.add(entry)
        await db.commit()


async def _agent_completed(company_id: str, agent_name: str) -> bool:
    """Return True if a successful research record exists for this agent + company."""
    from app.models.research import Research

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count())
            .select_from(Research)
            .where(Research.company_id == company_id)
            .where(Research.agent_name == agent_name)
        )
        return (result.scalar() or 0) > 0


async def identify_and_rescue(
    ctx,
    failed_agent_name: str,
    company_id: str,
    pipeline_run_id: str,
    resume_text: str = "",
    opportunity_id: str | None = None,
) -> bool:
    """
    Called by any agent job when it catches an unrecoverable error after all
    internal retries are exhausted.

    Logic:
    - Find which step failed
    - If it's a retry-eligible agent, re-enqueue the same job
    - Log the supervision event
    - Return True if a rescue job was enqueued, False if we gave up
    """
    logger.warning(
        "[SUPERVISOR] Identifying failure for %s on company %s",
        failed_agent_name,
        company_id,
    )

    # Check whether it truly hasn't completed (race-condition guard)
    if await _agent_completed(company_id, failed_agent_name):
        logger.info(
            "[SUPERVISOR] %s already has a research record for company %s — no rescue needed",
            failed_agent_name,
            company_id,
        )
        return False

    pool = ctx.get("redis")
    if pool is None:
        logger.error("[SUPERVISOR] No redis pool in ctx — cannot re-enqueue")
        return False

    # Map research name → arq job name
    job_map = {rn: jn for rn, jn in AGENT_CHAIN}
    arq_job = job_map.get(failed_agent_name)

    if arq_job is None:
        logger.error("[SUPERVISOR] Unknown agent name: %s", failed_agent_name)
        return False

    # Re-enqueue with appropriate args depending on agent
    if failed_agent_name == "agent5_pow" and opportunity_id:
        await pool.enqueue_job(arq_job, opportunity_id, company_id, pipeline_run_id, resume_text)
    else:
        await pool.enqueue_job(arq_job, company_id, pipeline_run_id, resume_text)

    action = f"rescue_re-enqueue:{arq_job}"
    await _log_supervision_event(company_id, failed_agent_name, action)

    logger.warning(
        "[SUPERVISOR] Rescue job enqueued: %s for company %s",
        arq_job,
        company_id,
    )
    return True


async def scan_stuck_companies(ctx, pipeline_run_id: str, resume_text: str = "") -> int:
    """
    Periodic sweep: find companies whose last research record is older than
    STUCK_THRESHOLD_SECONDS and that haven't completed the full chain.
    Re-enqueues the next missing agent for each stuck company.
    Returns the number of companies rescued.
    """
    from app.models.company import Company
    from app.models.research import Research

    cutoff = datetime.now(timezone.utc) - timedelta(seconds=STUCK_THRESHOLD_SECONDS)
    rescued = 0

    async with AsyncSessionLocal() as db:
        # Companies belonging to this pipeline that are still processing
        companies_result = await db.execute(
            select(Company).where(
                Company.pipeline_run_id == pipeline_run_id,
                Company.status == "processing",
            )
        )
        companies = companies_result.scalars().all()

    for company in companies:
        cid = str(company.id)

        # Find which agents have already run
        async with AsyncSessionLocal() as db:
            done_result = await db.execute(
                select(Research.agent_name)
                .where(Research.company_id == cid)
                .where(Research.agent_name != "supervisor")
            )
            done_agents = {row[0] for row in done_result.all()}

        # Find the first missing agent in the chain
        missing = None
        for agent_name, arq_job in AGENT_CHAIN:
            if agent_name not in done_agents:
                missing = (agent_name, arq_job)
                break

        if missing is None:
            # All agents done but status still 'processing' — mark complete
            from app.database import AsyncSessionLocal as ALS
            async with ALS() as db:
                result = await db.execute(select(Company).where(Company.id == company.id))
                c = result.scalar_one_or_none()
                if c:
                    c.status = "processed"
                    await db.commit()
            continue

        agent_name, arq_job = missing
        pool = ctx.get("redis")
        if pool:
            await pool.enqueue_job(arq_job, cid, pipeline_run_id, resume_text)
            await _log_supervision_event(cid, agent_name, f"stuck_sweep_rescue:{arq_job}")
            logger.warning(
                "[SUPERVISOR] Swept stuck company %s — re-enqueued %s",
                cid,
                arq_job,
            )
            rescued += 1

    return rescued
