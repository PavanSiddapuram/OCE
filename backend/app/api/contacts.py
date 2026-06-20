import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactOut, ContactStatusUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])

VALID_STATUSES = {"not_contacted", "messaged", "replied", "meeting", "interview", "offer"}


@router.post("", response_model=ContactOut, status_code=201)
async def create_contact(payload: ContactCreate, db: AsyncSession = Depends(get_db)):
    contact = Contact(**payload.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.patch("/{contact_id}/status", response_model=ContactOut)
async def update_contact_status(contact_id: uuid.UUID, payload: ContactStatusUpdate, db: AsyncSession = Depends(get_db)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {VALID_STATUSES}")

    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.status = payload.status
    await db.commit()
    await db.refresh(contact)
    return contact
