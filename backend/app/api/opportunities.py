import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
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


@router.post("/{opportunity_id}/pressure-test", response_model=OpportunityOut)
async def pressure_test_opportunity(opportunity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Run the agent9 gauntlet on this opportunity's PoW; returns the updated row.

    Synchronous by design — a single LLM call the engineer waits on before
    deciding whether to spend a weekend building.
    """
    result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    from app.agents.agent9_pressure_test import run_pressure_test
    verdict = await run_pressure_test(str(opportunity_id))
    if verdict is None:
        raise HTTPException(status_code=500, detail="Pressure test failed to produce a verdict")

    await db.refresh(opp)
    return opp
