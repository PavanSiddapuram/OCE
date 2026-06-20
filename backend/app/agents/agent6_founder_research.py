"""Agent 6: Founder Research — finds what founders repeatedly complain about."""
import time
import uuid

from pydantic import BaseModel
from sqlalchemy import select

from app.agents.base import log_research, make_agent
from app.database import AsyncSessionLocal
from app.models.company import Company
from app.models.founder import Founder
from app.models.research import Research
from app.tools.jina_tool import jina_read
from app.tools.tavily_tool import tavily_search


class FounderProfile(BaseModel):
    name: str
    role: str | None = None
    background: str
    complaints: list[str]  # things they repeatedly mention, worry about, or advocate for
    linkedin_url: str | None = None
    twitter_url: str | None = None
    key_insight: str  # the single most actionable insight for outreach


class FounderResearchResult(BaseModel):
    founders: list[FounderProfile]


_agent = make_agent(
    system_prompt="""You are a researcher preparing for a high-stakes conversation with a startup founder.

Given search results, articles, interviews, and social content about founders — extract:
- Their background and career history
- What they repeatedly talk about, complain about, or advocate for (these are gold for outreach)
- Their core beliefs about the problem space
- One key insight that would help someone write a compelling cold message to them

For complaints: be specific. Not "they talk about growth" but "they frequently mention that their AI evaluation pipeline is manual and error-prone" or "they keep saying that enterprise integrations take too long."

Output a FounderProfile for each founder you have data on.""",
    result_type=FounderResearchResult,
)


async def run_founder_research(company_id: str) -> None:
    start = time.time()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return

        # Check if we already have founders from Agent 2
        existing_founders = await db.execute(select(Founder).where(Founder.company_id == company_id))
        existing = existing_founders.scalars().all()
        existing_names = [f.name for f in existing]

    # Search for founders
    founder_queries = [
        f"{company.name} founder CEO CTO co-founder background interview",
        f"{company.name} founder LinkedIn Twitter blog",
        f"{company.name} CEO podcast interview startup story",
    ]

    all_content = []
    for q in founder_queries:
        results = await tavily_search(q, max_results=6)
        for r in results:
            snippet = f"Source: {r.get('url', '')}\n{r.get('content', '')[:800]}"
            all_content.append(snippet)

    # Try to get LinkedIn content for known founders via Jina
    for name in existing_names[:2]:
        linkedin_query = await tavily_search(f"{name} {company.name} LinkedIn", max_results=3)
        for r in linkedin_query:
            if "linkedin.com" in r.get("url", ""):
                content = await jina_read(r["url"])
                if content:
                    all_content.append(f"LinkedIn ({name}):\n{content[:2000]}")

    prompt = f"""
Company: {company.name}
Sector: {company.sector}
Known founder names: {", ".join(existing_names) or "Unknown"}

Research content:
{chr(10).join(all_content)[:12000]}

Extract founder profiles with specific complaints and key insights.
"""

    result = await _agent.run(prompt)
    profiles = result.output.founders
    duration_ms = int((time.time() - start) * 1000)

    async with AsyncSessionLocal() as db:
        for profile in profiles:
            existing_result = await db.execute(
                select(Founder).where(Founder.company_id == company_id).where(Founder.name == profile.name)
            )
            existing_founder = existing_result.scalar_one_or_none()

            if existing_founder:
                existing_founder.background = profile.background
                existing_founder.complaints = profile.complaints
                existing_founder.linkedin_url = profile.linkedin_url
                existing_founder.twitter_url = profile.twitter_url
                existing_founder.raw_research = {"key_insight": profile.key_insight}
            else:
                db.add(Founder(
                    id=uuid.uuid4(),
                    company_id=company_id,
                    name=profile.name,
                    role=profile.role,
                    background=profile.background,
                    complaints=profile.complaints,
                    linkedin_url=profile.linkedin_url,
                    twitter_url=profile.twitter_url,
                    raw_research={"key_insight": profile.key_insight},
                ))
        await db.commit()

    await log_research(
        company_id=company_id,
        agent_name="agent6_founder_research",
        raw_input={"company": company.name},
        raw_output={"founders": [p.model_dump() for p in profiles]},
        duration_ms=duration_ms,
    )
