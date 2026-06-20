import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyDetail, CompanyOut, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=dict)
async def list_companies(
    city: str | None = None,
    sector: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Company)
    if city:
        query = query.where(Company.city.ilike(f"%{city}%"))
    if sector:
        query = query.where(Company.sector.ilike(f"%{sector}%"))
    if status:
        query = query.where(Company.status == status)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.offset((page - 1) * limit).limit(limit).order_by(Company.created_at.desc())
    result = await db.execute(query)
    companies = result.scalars().all()

    return {"items": [CompanyOut.model_validate(c) for c in companies], "total": total, "page": page}


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Company)
        .options(
            selectinload(Company.opportunities),
            selectinload(Company.founders),
            selectinload(Company.outreach),
            selectinload(Company.contacts),
        )
        .where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyOut)
async def update_company(company_id: uuid.UUID, update: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for field, value in update.model_dump(exclude_none=True).items():
        setattr(company, field, value)

    await db.commit()
    await db.refresh(company)
    return company
