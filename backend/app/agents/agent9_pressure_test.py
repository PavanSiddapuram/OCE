"""Agent 9: Pressure Test — adversarial gate before committing a weekend to a PoW idea.

Condensed Paul-Graham-style gauntlet (assumption / flaws / cuts) adapted from
startup scale to weekend-prototype scale. Runs on demand per opportunity, not
in the automatic pipeline — the scarce resource it protects is the engineer's
build time, so the engineer pulls the trigger.
"""
import time
import uuid
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import select

from app.agents.base import log_research, make_agent, run_agent_with_retry
from app.database import AsyncSessionLocal
from app.models.company import Company
from app.models.opportunity import Opportunity


class FatalFlaw(BaseModel):
    label: str  # 3-word label
    why_it_kills: str  # why this kills THIS PoW specifically
    what_overcomes: str  # what would have to be true to survive it


class PressureTestResult(BaseModel):
    core_assumption: str  # single falsifiable assumption behind this PoW
    fatal_flaws: list[FatalFlaw]  # ranked, most dangerous first (2-3)
    founder_shrug_risk: str  # the current behavior/workaround that makes the founder ignore this
    cuts_for_weekend: list[str]  # features to cut so it ships in ONE weekend
    verdict: Literal["BUILD", "RESHAPE", "SKIP"]
    verdict_reasoning: str  # one paragraph, no hedging


_agent = make_agent(
    system_prompt="""You are a composite evaluator: Paul Graham reviewing a proof-of-work project,
plus a founder who receives 50 cold outreach messages a week and ignores 49 of them.
You have zero patience for prototypes that sound impressive but wouldn't change a founder's mind.

Context: an engineer is about to spend ONE weekend building a mini-project (proof-of-work)
targeted at a specific startup, then send it to the founder to create a job opportunity
that doesn't exist yet. Your job is to find every reason this specific PoW fails BEFORE
the weekend is spent. This is not a startup — do not evaluate market size or business
model. Evaluate: will THIS founder, at THIS company, actually care about THIS artifact?

Produce:
1. core_assumption — the single falsifiable assumption that must be true for this PoW
   to impress this founder. One sentence.
2. fatal_flaws — 2-3 flaws ranked most dangerous first. Each: a 3-word label, why it
   kills THIS PoW specifically (not generic advice), and what would have to be true
   to overcome it.
3. founder_shrug_risk — the current behavior, tool, or workaround the founder already
   has that makes this PoW easy to ignore. Name the real enemy: a habit, not a company.
4. cuts_for_weekend — at least 3 things an eager engineer would build that must be CUT
   so this ships in one weekend. Each cut must state why it would delay or dilute the test.
5. verdict — BUILD (worth the weekend as-is), RESHAPE (right target, wrong artifact —
   the flaws show how), or SKIP (this founder won't care, spend the weekend elsewhere).
6. verdict_reasoning — one paragraph. No hedging. No "it has potential." State the
   exact reason for the verdict.

Be specific to the company and opportunity in every point. Generic startup advice is a failure.""",
    result_type=PressureTestResult,
)


async def run_pressure_test(opportunity_id: str) -> dict | None:
    """Run the gauntlet on one opportunity's PoW; persist verdict on the row."""
    start = time.time()

    async with AsyncSessionLocal() as db:
        opp_result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
        opp = opp_result.scalar_one_or_none()
        if not opp:
            return None
        company_result = await db.execute(select(Company).where(Company.id == opp.company_id))
        company = company_result.scalar_one_or_none()

    prompt = f"""
Company: {company.name if company else "Unknown"}
Mission: {company.mission if company else "Unknown"}
Product: {company.product_summary if company else "Unknown"}
Tech Stack: {", ".join(company.tech_stack or []) if company else "Unknown"}
Current Focus: {company.current_focus if company else "Unknown"}

Opportunity ({opp.category}):
Title: {opp.title}
Description: {opp.description}
Impact: {opp.impact}
Fit score for this engineer: {opp.fit_score}/100 — {opp.fit_reasoning}

Proposed proof-of-work to pressure test:
{opp.pow_idea or "No PoW idea generated yet — evaluate the opportunity itself as a build target."}

Pressure test this proof-of-work before the engineer commits a weekend to it.
"""

    result = await run_agent_with_retry(_agent, prompt)
    verdict = result.output
    duration_ms = int((time.time() - start) * 1000)

    verdict_dict = verdict.model_dump()
    async with AsyncSessionLocal() as db:
        opp_result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
        opp = opp_result.scalar_one_or_none()
        if opp:
            opp.pressure_test = verdict_dict
            await db.commit()

    await log_research(
        company_id=str(opp.company_id),
        agent_name="agent9_pressure_test",
        raw_input={"opportunity_id": str(opportunity_id), "title": opp.title},
        raw_output=verdict_dict,
        duration_ms=duration_ms,
    )

    return verdict_dict
