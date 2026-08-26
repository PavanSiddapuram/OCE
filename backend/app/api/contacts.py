import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.opportunity import Opportunity
from app.schemas.contact import ContactCreate, ContactOut, ContactStatusUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contacts", tags=["contacts"])

VALID_STATUSES = {"not_contacted", "messaged", "replied", "meeting", "interview", "offer"}

# Positive signals: when a contact advances to these stages boost opportunity scores
# so future pipeline runs rank similar companies higher.
_SIGNAL_BOOSTS: dict[str, int] = {
    "replied":   3,
    "meeting":   6,
    "interview": 10,
    "offer":     15,
}


async def _apply_crm_signal(company_id: uuid.UUID, new_status: str, db: AsyncSession) -> None:
    """
    Feedback loop: when a contact advances to a positive CRM stage, nudge
    fit_scores on that company's opportunities upward so the pipeline learns
    which companies are genuinely responsive.

    The boost is small (≤15 pts) and capped at 100 so it can't manufacture
    false positives — it only amplifies signal already present.
    """
    boost = _SIGNAL_BOOSTS.get(new_status, 0)
    if boost == 0:
        return

    result = await db.execute(
        select(Opportunity).where(Opportunity.company_id == company_id)
    )
    opportunities = result.scalars().all()
    for opp in opportunities:
        if opp.fit_score is not None:
            opp.fit_score = min(100, opp.fit_score + boost)
            db.add(opp)

    if opportunities:
        logger.info(
            "[CRM] Applied +%d fit_score boost to %d opportunities for company %s (status → %s)",
            boost, len(opportunities), company_id, new_status,
        )


@router.post("", response_model=ContactOut, status_code=201)
async def create_contact(payload: ContactCreate, db: AsyncSession = Depends(get_db)):
    contact = Contact(**payload.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.patch("/{contact_id}/status", response_model=ContactOut)
async def update_contact_status(
    contact_id: uuid.UUID,
    payload: ContactStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {VALID_STATUSES}")

    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    old_status = contact.status
    contact.status = payload.status

    # Apply fit_score feedback only on forward advancement (not rollbacks)
    STATUS_ORDER = list(VALID_STATUSES)  # insertion order matches pipeline flow
    status_rank = {s: i for i, s in enumerate(
        ["not_contacted", "messaged", "replied", "meeting", "interview", "offer"]
    )}
    advancing = status_rank.get(payload.status, 0) > status_rank.get(old_status, 0)
    if advancing:
        await _apply_crm_signal(contact.company_id, payload.status, db)

    await db.commit()
    await db.refresh(contact)
    return contact
