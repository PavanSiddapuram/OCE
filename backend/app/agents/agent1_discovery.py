"""Agent 1: Startup Discovery — finds real startups from YC, Accel, Peak XV, Blume, etc."""
import time
import uuid
from urllib.parse import urlparse

from pydantic import BaseModel
from sqlalchemy import select

from app.agents.base import log_research, make_agent, run_agent_with_retry
from app.database import AsyncSessionLocal
from app.models.company import Company
from app.tools.tavily_tool import tavily_search


class CompanyStub(BaseModel):
    name: str
    website: str
    source: str  # yc | accel | peak_xv | nexus | blume | angellist | crunchbase
    source_url: str = ""
    city: str | None = None
    sector: str | None = None
    stage: str | None = None


class DiscoveryResult(BaseModel):
    companies: list[CompanyStub]


_agent = make_agent(
    system_prompt="""You are a startup researcher. Given search results from YC, Accel, Peak XV, Nexus, Blume, AngelList and Crunchbase, extract a list of real startups.

Rules:
- Only include companies you can identify from the search results. Never hallucinate.
- Deduplicate by website domain.
- Extract: name, website (full URL), source (yc/accel/peak_xv/nexus/blume/angellist/crunchbase), source_url, city, sector, stage.
- Stage: pre-seed, seed, series-a, series-b, growth, or null if unknown.
- Sector: use the sector filter if unclear from results.""",
    result_type=DiscoveryResult,
)


def _normalize_domain(url: str) -> str:
    """Return bare domain (no scheme, no www, no trailing slash) for dedup."""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain = parsed.netloc or parsed.path
        return domain.lower().removeprefix("www.")
    except Exception:
        return url.lower()


async def run_discovery(city: str, sector: str, max_companies: int, pipeline_run_id: str) -> list[uuid.UUID]:
    """Run Agent 1. Returns list of company UUIDs inserted into DB."""
    start = time.time()

    queries = [
        f"YC Y Combinator portfolio startups {city} {sector}",
        f"Accel portfolio companies {city} {sector} startup 2023 2024",
        f"Peak XV Nexus Blume portfolio {city} {sector} startup",
        f"site:angel.co {city} {sector} startup funding",
    ]

    search_results = []
    for q in queries:
        results = await tavily_search(q, max_results=8)
        search_results.extend(results)

    prompt = f"""
City filter: {city}
Sector filter: {sector}
Max companies to return: {max_companies}

Search results (title, url, snippet):
{_format_results(search_results)}

Extract up to {max_companies} distinct startups matching the city and sector filters.
"""

    result = await run_agent_with_retry(_agent, prompt)
    companies = result.output.companies[:max_companies]

    duration_ms = int((time.time() - start) * 1000)
    inserted_ids: list[uuid.UUID] = []

    # Pre-load all existing domains for O(1) dedup without per-row DB round trips
    async with AsyncSessionLocal() as db:
        existing_rows = await db.execute(select(Company.website))
        existing_domains: set[str] = {
            _normalize_domain(w) for w in existing_rows.scalars().all() if w
        }

        # Second-pass dedup within the batch returned by the LLM
        seen_in_batch: set[str] = set()

        for stub in companies:
            domain = _normalize_domain(stub.website)
            if domain in existing_domains or domain in seen_in_batch:
                continue
            seen_in_batch.add(domain)

            company = Company(
                name=stub.name,
                website=stub.website,
                source=stub.source,
                source_url=stub.source_url,
                city=stub.city or city,
                sector=stub.sector or sector,
                stage=stub.stage,
                status="discovered",
                pipeline_run_id=uuid.UUID(str(pipeline_run_id)),
            )
            db.add(company)
            await db.flush()
            inserted_ids.append(company.id)

        await db.commit()

    if inserted_ids:
        await log_research(
            company_id=str(inserted_ids[0]),
            agent_name="agent1_discovery",
            raw_input={"city": city, "sector": sector, "queries": queries},
            raw_output={"companies_found": len(companies), "inserted": len(inserted_ids)},
            tokens_used=None,
            duration_ms=duration_ms,
        )

    return inserted_ids


def _format_results(results: list[dict]) -> str:
    lines = []
    for r in results[:30]:
        lines.append(f"- {r.get('title', '')} | {r.get('url', '')} | {r.get('content', '')[:200]}")
    return "\n".join(lines)
