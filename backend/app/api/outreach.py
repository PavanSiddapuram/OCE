import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.outreach import Outreach
from app.schemas.outreach import OutreachOut

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.get("/{company_id}")
async def get_company_outreach(company_id: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Outreach).where(Outreach.company_id == uuid.UUID(company_id)).order_by(Outreach.created_at.desc())
        )
        items = result.scalars().all()
        if items:
            return [OutreachOut.model_validate(i) for i in items]
    except Exception:
        pass
    return []


@router.get("")
async def list_all_outreach(
    channel: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Outreach).order_by(Outreach.created_at.desc())
        if channel:
            query = query.where(Outreach.channel == channel)
        result = await db.execute(query)
        items = result.scalars().all()
        if items:
            return [OutreachOut.model_validate(i) for i in items]
    except Exception:
        pass
    return []
