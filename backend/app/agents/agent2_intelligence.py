"""Agent 2: Company Intelligence — scrapes website, blogs, hiring page, founder interviews."""
import time

from pydantic import BaseModel
from sqlalchemy import select

from app.agents.base import log_research, make_agent
from app.database import AsyncSessionLocal
from app.models.company import Company
from app.tools.firecrawl_tool import firecrawl_scrape
from app.tools.tavily_tool import tavily_search


class CompanyIntel(BaseModel):
    mission: str | None = None
    product_summary: str
    recent_launches: list[str]
    tech_stack: list[str]
    current_focus: str | None = None
    founders: list[str] = []  # founder names discovered


_agent = make_agent(
    system_prompt="""You are a company analyst. Given scraped web content from a startup's website, blog, changelog, and hiring page — extract structured intelligence.

Output:
- mission: 1-2 sentence mission statement
- product_summary: 2-3 sentence description of what the product does
- recent_launches: list of recent features/products launched (max 5)
- tech_stack: list of technologies you can infer from job descriptions or technical pages
- current_focus: what the company is currently focused on building or expanding
- founders: list of founder names you can identify

Be accurate. Only include things you can infer from the provided content. Do not hallucinate.""",
    result_type=CompanyIntel,
)


async def run_intelligence(company_id: str) -> None:
    start = time.time()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company or not company.website:
            return
        name = company.name
        website = company.website.rstrip("/")

    pages = [
        website,
        f"{website}/blog",
        f"{website}/changelog",
        f"{website}/careers",
        f"{website}/about",
    ]

    scraped_content = []
    for page in pages:
        content = await firecrawl_scrape(page)
        if content:
            scraped_content.append(f"## {page}\n{content[:3000]}")

    # Also search for founder interviews
    interview_results = await tavily_search(f"{name} founder CEO interview podcast blog", max_results=5)
    interview_snippets = "\n".join(
        f"- {r.get('title')}: {r.get('content', '')[:300]}" for r in interview_results
    )

    prompt = f"""
Company: {name}
Website: {website}

Scraped content from their website:
{chr(10).join(scraped_content[:15000])}

Interview/podcast search results:
{interview_snippets}

Extract structured intelligence about this company.
"""

    intel_result = await _agent.run(prompt)
    intel = intel_result.output
    duration_ms = int((time.time() - start) * 1000)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if company:
            company.mission = intel.mission
            company.product_summary = intel.product_summary
            company.recent_launches = intel.recent_launches
            company.tech_stack = intel.tech_stack
            company.current_focus = intel.current_focus
            company.status = "intel_done"
            await db.commit()

    await log_research(
        company_id=company_id,
        agent_name="agent2_intelligence",
        raw_input={"website": website, "pages_scraped": pages},
        raw_output=intel.model_dump(),
        duration_ms=duration_ms,
    )
