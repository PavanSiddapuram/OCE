import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityOut

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=dict)
async def list_opportunities(
    company_id: uuid.UUID | None = None,
    category: str | None = None,
    min_score: int | None = None,
    sort: str = "fit_score",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import func
    query = select(Opportunity)

    if company_id:
        query = query.where(Opportunity.company_id == company_id)
    if category:
        query = query.where(Opportunity.category == category)
    if min_score is not None:
        query = query.where(Opportunity.fit_score >= min_score)

    if sort == "fit_score":
        query = query.order_by(Opportunity.fit_score.desc().nulls_last())
    else:
        query = query.order_by(Opportunity.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    opps = result.scalars().all()

    return {"items": [OpportunityOut.model_validate(o) for o in opps], "total": total, "page": page}
