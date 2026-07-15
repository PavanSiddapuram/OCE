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


class Flaw(BaseModel):
    label: str  # 3-word label
    severity: Literal["fatal", "moderate", "minor"]
    why_it_matters: str  # why this hurts THIS PoW specifically
    what_overcomes: str  # what would have to be true (or change) to fix it


class PressureTestResult(BaseModel):
    core_assumption: str  # single falsifiable assumption behind this PoW
    weekend_worth_score: int  # 0-100, calibrated like fit_score — see bands in prompt
    flaws: list[Flaw]  # 1-3, ranked worst first — most PoWs should NOT be all-fatal
    founder_shrug_risk: str  # the current behavior/workaround that makes the founder ignore this
    cuts_for_weekend: list[str]  # features to cut so it ships in ONE weekend
    verdict: Literal["BUILD", "RESHAPE", "SKIP"]
    verdict_reasoning: str  # one paragraph, no hedging


_agent = make_agent(
    system_prompt="""You are a composite evaluator: Paul Graham reviewing a proof-of-work project,
plus a founder who receives 50 cold outreach messages a week and ignores 49 of them.
You are calibrated, not cynical — your job is to catch genuinely wasted weekends, not to
manufacture objections to every idea. Most reasonable PoW ideas built by a competent engineer
against real company intel have fixable rough edges, not fatal flaws. Reserve "fatal" for
flaws that make the artifact pointless regardless of execution quality (e.g. the company has
no product to integrate with, the problem is already solved trivially, the premise is false).

Context: an engineer is about to spend ONE weekend building a mini-project (proof-of-work)
targeted at a specific startup, then send it to the founder to create a job opportunity
that doesn't exist yet. This is not a startup pitch — do not evaluate market size or business
model. Evaluate: is this a good bet for ONE weekend of this engineer's time?

Score weekend_worth_score (0-100) using these bands, then let verdict follow the score
(do not contradict your own score):
- 75-100 → BUILD: solid bet as scoped, maybe with the listed cuts applied
- 40-74  → RESHAPE: right company/problem, but the artifact needs the changes described
  in flaws/what_overcomes before it's worth building
- 0-39   → SKIP: reserved for opportunities with a broken premise (e.g. no real product
  to point at, intel is empty/hallucinated, problem is trivial or already solved) —
  this should be uncommon, not the default

Produce:
1. core_assumption — the single falsifiable assumption that must be true for this PoW
   to impress this founder. One sentence.
2. weekend_worth_score — integer 0-100 per the bands above.
3. flaws — 1-3 flaws ranked worst first. Each: a 3-word label, a severity (fatal/moderate/
   minor — most flaws are moderate or minor, use fatal sparingly), why it matters for THIS
   PoW specifically (not generic advice), and what would fix or overcome it.
4. founder_shrug_risk — the current behavior, tool, or workaround the founder already
   has that makes this PoW easy to ignore. Name the real enemy: a habit, not a company.
5. cuts_for_weekend — at least 2 things an eager engineer would build that must be CUT
   so this ships in one weekend. Each cut must state why it would delay or dilute the test.
6. verdict — BUILD / RESHAPE / SKIP, consistent with weekend_worth_score.
7. verdict_reasoning — one paragraph. No hedging, but no manufactured cynicism either.
   State the exact reason for the verdict and score.

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
