"""Agent 3: Opportunity Detection — thinks like a founder to find what an engineer can build."""
import time
import uuid
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import select

from app.agents.base import log_research, make_agent, run_agent_with_retry
from app.database import AsyncSessionLocal
from app.models.company import Company
from app.models.opportunity import Opportunity


class OpportunityDraft(BaseModel):
    title: str
    category: Literal["bottleneck", "growth_lever", "missing_piece", "technical_debt"]
    description: str
    impact: str
    skills_required: list[str]


class OpportunityAnalysis(BaseModel):
    opportunities: list[OpportunityDraft]


_agent = make_agent(
    system_prompt="""You are an experienced software-focused founder reviewing your own company.

Given a company's mission, product, tech stack, recent launches, and current focus — identify 3-5 specific things a skilled software engineer could build or improve that would meaningfully move the needle.

Categories:
- bottleneck: internal inefficiency slowing the team down (tooling, automation, observability)
- growth_lever: something that directly improves acquisition, activation, or retention
- missing_piece: integration, feature, or capability that competitors have or customers request
- technical_debt: architecture or code quality issue blocking velocity

For each opportunity:
- title: short, specific (e.g. "Build automated model evaluation pipeline")
- category: one of the four above
- description: 2-3 sentences explaining exactly what needs to be built
- impact: why this matters to the business (1-2 sentences)
- skills_required: 2-5 specific technical skills

Be specific to this company. Reference their actual stack, product, and focus area.""",
    result_type=OpportunityAnalysis,
)


async def run_opportunity_detection(company_id: str) -> None:
    start = time.time()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return

    prompt = f"""
Company: {company.name}
Mission: {company.mission or "Unknown"}
Product: {company.product_summary or "Unknown"}
Tech Stack: {", ".join(company.tech_stack or [])}
Recent Launches: {", ".join(company.recent_launches or [])}
Current Focus: {company.current_focus or "Unknown"}
Sector: {company.sector}

Identify 3-5 specific opportunities for a software engineer at this company.
"""

    result = await run_agent_with_retry(_agent, prompt)
    opportunities = result.output.opportunities
    duration_ms = int((time.time() - start) * 1000)

    async with AsyncSessionLocal() as db:
        for opp in opportunities:
            db.add(Opportunity(
                id=uuid.uuid4(),
                company_id=company_id,
                title=opp.title,
                category=opp.category,
                description=opp.description,
                impact=opp.impact,
                skills_required=opp.skills_required,
            ))
        company_result = await db.execute(select(Company).where(Company.id == company_id))
        company_row = company_result.scalar_one_or_none()
        if company_row:
            company_row.status = "analyzed"
        await db.commit()

    await log_research(
        company_id=company_id,
        agent_name="agent3_opportunity",
        raw_input={"company": company.name},
        raw_output={"opportunities": [o.model_dump() for o in opportunities]},
        duration_ms=duration_ms,
    )
