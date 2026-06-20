"""Agent 7: Narrative Agent — writes founder-specific outreach messages."""
import time
import uuid

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.agents.base import log_research, make_agent
from app.database import AsyncSessionLocal
from app.models.company import Company
from app.models.contact import Contact
from app.models.founder import Founder
from app.models.opportunity import Opportunity
from app.models.outreach import Outreach


class OutreachDraft(BaseModel):
    channel: str  # linkedin | email | twitter
    subject: str | None = None
    hook: str  # opening line referencing something real the founder said
    why_company: str
    why_problem: str
    why_me: str
    what_i_built: str  # references the PoW idea
    call_to_action: str
    body: str  # full assembled message


class NarrativeResult(BaseModel):
    outreach_messages: list[OutreachDraft]


_agent = make_agent(
    system_prompt="""You are a master at writing founder-specific cold outreach that gets replies.

Your messages are NOT generic cold emails. They are peer-to-peer, specific, and show you've done real work.

Structure of a great outreach message:
1. hook: Reference something specific the founder said, wrote, or built. Not "I love what you're doing." Something like "Your post about evaluation being the bottleneck for AI in production resonated — I've hit that exact wall."
2. why_company: 1-2 sentences on why THIS company specifically (reference their mission/focus)
3. why_problem: 1-2 sentences on why YOU care about this specific problem
4. why_me: 2-3 sentences on your relevant background and what makes you different
5. what_i_built: Reference the proof-of-work project — describe it in 1-2 lines, include what it shows
6. call_to_action: Soft, specific ask — not "let me know if you're hiring" but "happy to walk you through what I built over a 20-min call if it's useful"

Tone: Confident, peer-to-peer. You are NOT a job seeker. You are an engineer who spotted a real problem and built something to solve it.

Generate outreach for LinkedIn (short, <250 words), email (medium, <400 words), and Twitter DM (very short, <100 words).""",
    result_type=NarrativeResult,
)


async def run_narrative(company_id: str, resume_text: str) -> None:
    start = time.time()

    async with AsyncSessionLocal() as db:
        company_result = await db.execute(
            select(Company)
            .options(selectinload(Company.founders), selectinload(Company.opportunities))
            .where(Company.id == company_id)
        )
        company = company_result.scalar_one_or_none()
        if not company:
            return

    # Get top opportunity
    top_opp = max(
        (o for o in company.opportunities if o.fit_score is not None),
        key=lambda o: o.fit_score,
        default=None,
    ) if company.opportunities else None

    # Get top founder complaint
    top_founder = company.founders[0] if company.founders else None
    founder_complaint = (top_founder.complaints[0] if top_founder and top_founder.complaints else None)
    founder_insight = (top_founder.raw_research.get("key_insight") if top_founder and top_founder.raw_research else None)

    prompt = f"""
Company: {company.name}
Mission: {company.mission or ""}
Current Focus: {company.current_focus or ""}

Top Opportunity:
{f"Title: {top_opp.title}" if top_opp else "No opportunity scored yet"}
{f"Description: {top_opp.description}" if top_opp else ""}
{f"PoW: {top_opp.pow_idea}" if top_opp else ""}

Founder: {top_founder.name if top_founder else "Unknown"}
Founder Complaint: {founder_complaint or "Not found"}
Key Insight: {founder_insight or "Not found"}

Engineer's Resume (abbreviated):
{resume_text[:3000]}

Write outreach messages for LinkedIn, email, and Twitter DM.
Reference the founder's complaint in the hook. Reference the PoW project in what_i_built.
"""

    result = await _agent.run(prompt)
    messages = result.output.outreach_messages
    duration_ms = int((time.time() - start) * 1000)

    async with AsyncSessionLocal() as db:
        for msg in messages:
            outreach = Outreach(
                id=uuid.uuid4(),
                company_id=company_id,
                opportunity_id=top_opp.id if top_opp else None,
                channel=msg.channel,
                subject=msg.subject,
                hook=msg.hook,
                why_company=msg.why_company,
                why_problem=msg.why_problem,
                why_me=msg.why_me,
                what_i_built=msg.what_i_built,
                call_to_action=msg.call_to_action,
                body=msg.body,
            )
            db.add(outreach)

        company_result = await db.execute(select(Company).where(Company.id == company_id))
        company_row = company_result.scalar_one_or_none()
        if company_row:
            company_row.status = "outreach_ready"
        await db.commit()

    await log_research(
        company_id=company_id,
        agent_name="agent7_narrative",
        raw_input={"company": company.name, "channels": [m.channel for m in messages]},
        raw_output={"messages_generated": len(messages)},
        duration_ms=duration_ms,
    )
