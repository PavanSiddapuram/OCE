import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.outreach import Outreach
from app.schemas.outreach import OutreachOut

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.get("/{company_id}", response_model=list[OutreachOut])
async def get_company_outreach(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Outreach).where(Outreach.company_id == company_id).order_by(Outreach.created_at.desc())
    )
    return result.scalars().all()


@router.get("", response_model=list[OutreachOut])
async def list_all_outreach(
    channel: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Outreach).order_by(Outreach.created_at.desc())
    if channel:
        query = query.where(Outreach.channel == channel)
    result = await db.execute(query)
    return result.scalars().all()
