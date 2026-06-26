"""Agent 4: Skill Match Engine — scores how well the engineer fits each opportunity."""
import time
import uuid

from pydantic import BaseModel
from sqlalchemy import select

from app.agents.base import log_research, make_agent, run_agent_with_retry
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.opportunity import Opportunity


class SkillMatchResult(BaseModel):
    opportunity_title: str
    fit_score: int  # 0-100
    fit_reasoning: str


class BatchSkillMatch(BaseModel):
    matches: list[SkillMatchResult]


_agent = make_agent(
    system_prompt="""You are a calibrated talent evaluator.

For each opportunity, score how well the provided engineer resume matches (0-100):
- 80-100: strong fit — engineer has direct experience with the core skills
- 60-79: decent fit — engineer has transferable skills, can likely do this
- 40-59: stretch — engineer would need to learn key skills
- 0-39: poor fit — significant skill gap

Scoring weights:
- Direct skill overlap: 40%
- Domain/sector experience: 20%
- Evidence of shipping similar things: 30%
- Communication/ownership signals: 10%

For each match, provide:
- opportunity_title: exact title from the opportunity
- fit_score: integer 0-100
- fit_reasoning: 2-3 sentences explaining the score

Be calibrated and honest. Do not inflate scores.""",
    result_type=BatchSkillMatch,
)


async def run_skill_match(company_id: str, resume_text: str) -> list[uuid.UUID]:
    """Returns IDs of top N opportunities (sorted by fit_score)."""
    start = time.time()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Opportunity).where(Opportunity.company_id == company_id))
        opportunities = result.scalars().all()

    if not opportunities:
        return []

    opp_descriptions = "\n\n".join(
        f"Title: {o.title}\nCategory: {o.category}\nDescription: {o.description}\nSkills Required: {', '.join(o.skills_required or [])}"
        for o in opportunities
    )

    prompt = f"""
Engineer's Resume:
{resume_text}

Opportunities to score:
{opp_descriptions}

Score each opportunity for fit with this engineer.
"""

    result = await run_agent_with_retry(_agent, prompt)
    matches = result.output.matches
    duration_ms = int((time.time() - start) * 1000)

    score_map = {m.opportunity_title.lower().strip(): m for m in matches}

    async with AsyncSessionLocal() as db:
        for opp in opportunities:
            match = score_map.get(opp.title.lower().strip())
            if match:
                opp.fit_score = match.fit_score
                opp.fit_reasoning = match.fit_reasoning
                db.add(opp)
        await db.commit()

    await log_research(
        company_id=company_id,
        agent_name="agent4_skill_match",
        raw_input={"opportunity_count": len(opportunities)},
        raw_output={"matches": [m.model_dump() for m in matches]},
        duration_ms=duration_ms,
    )

    top_n = settings.top_opportunities_for_pow
    scored = [(o.id, o.fit_score or 0) for o in opportunities]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [oid for oid, _ in scored[:top_n]]
