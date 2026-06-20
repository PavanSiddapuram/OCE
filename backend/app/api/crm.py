from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactOut

router = APIRouter(prefix="/crm", tags=["crm"])

CRM_STATUSES = ["not_contacted", "messaged", "replied", "meeting", "interview", "offer"]


@router.get("/board")
async def get_crm_board(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Contact).options(selectinload(Contact.company)).order_by(Contact.updated_at.desc())
    )
    contacts = result.scalars().all()

    board: dict[str, list] = {s: [] for s in CRM_STATUSES}
    for contact in contacts:
        status = contact.status if contact.status in board else "not_contacted"
        board[status].append(ContactOut.model_validate(contact))

    return board
