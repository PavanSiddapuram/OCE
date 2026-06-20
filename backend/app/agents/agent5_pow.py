"""Agent 5: Proof-of-Work Generator — designs a concrete mini-project per opportunity."""
import time

from pydantic import BaseModel
from sqlalchemy import select

from app.agents.base import log_research, make_agent
from app.database import AsyncSessionLocal
from app.models.opportunity import Opportunity
from app.models.company import Company


class ProofOfWorkIdea(BaseModel):
    name: str
    description: str  # 3-bullet description
    rough_structure: str  # key files/components
    estimated_hours: str  # e.g. "8-12 hours"
    why_impressive: str  # why a founder would care about this


_agent = make_agent(
    system_prompt="""You are a senior engineer who builds impressive proof-of-work projects to get hired at startups.

Given an opportunity at a specific company, design a mini-project that:
1. Directly demonstrates you can solve the stated problem
2. Can be built in a weekend (8-24 hours)
3. Would make the founder say "this person gets it"

Output:
- name: short project name (e.g. "Sarvam Eval Dashboard")
- description: 3 bullet points describing what it does
- rough_structure: key files, components, or architecture (3-5 lines)
- estimated_hours: realistic time estimate (e.g. "10-15 hours")
- why_impressive: 1-2 sentences on why a founder at this company would be impressed

Be specific to the company and opportunity. Reference their actual tech stack if known.""",
    result_type=ProofOfWorkIdea,
)


async def run_pow_generation(opportunity_id: str) -> None:
    start = time.time()

    async with AsyncSessionLocal() as db:
        opp_result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
        opp = opp_result.scalar_one_or_none()
        if not opp:
            return

        company_result = await db.execute(select(Company).where(Company.id == opp.company_id))
        company = company_result.scalar_one_or_none()

    prompt = f"""
Company: {company.name if company else "Unknown"}
Tech Stack: {", ".join(company.tech_stack or []) if company else "Unknown"}
Current Focus: {company.current_focus if company else "Unknown"}

Opportunity:
Title: {opp.title}
Category: {opp.category}
Description: {opp.description}
Impact: {opp.impact}
Skills Required: {", ".join(opp.skills_required or [])}

Design a proof-of-work mini-project for this specific opportunity.
"""

    result = await _agent.run(prompt)
    idea = result.output
    duration_ms = int((time.time() - start) * 1000)

    pow_text = f"""**{idea.name}** ({idea.estimated_hours})

{idea.description}

Structure: {idea.rough_structure}

Why it matters: {idea.why_impressive}"""

    async with AsyncSessionLocal() as db:
        opp_result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
        opp = opp_result.scalar_one_or_none()
        if opp:
            opp.pow_idea = pow_text
            await db.commit()

    await log_research(
        company_id=str(opp.company_id),
        agent_name="agent5_pow",
        raw_input={"opportunity_id": opportunity_id, "title": opp.title},
        raw_output=idea.model_dump(),
        duration_ms=duration_ms,
    )
