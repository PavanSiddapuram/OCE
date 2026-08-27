from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.app_state import AppState
from app.schemas.app_state import AppStateIn, AppStateOut

router = APIRouter(prefix="/state", tags=["app-state"])


@router.get("/{key}", response_model=AppStateOut)
async def get_state(key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppState).where(AppState.key == key))
    state = result.scalar_one_or_none()
    if not state:
        raise HTTPException(status_code=404, detail=f"No state stored for key '{key}'")
    return state


@router.put("/{key}", response_model=AppStateOut)
async def put_state(key: str, payload: AppStateIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppState).where(AppState.key == key))
    state = result.scalar_one_or_none()
    if state:
        state.value = payload.value
    else:
        state = AppState(key=key, value=payload.value)
        db.add(state)
    await db.commit()
    await db.refresh(state)
    return state
