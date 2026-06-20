import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.pipeline_run import PipelineRun
from app.schemas.pipeline import PipelineRunRequest, PipelineRunResponse, PipelineStatusResponse

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse)
async def run_pipeline(request: PipelineRunRequest, db: AsyncSession = Depends(get_db)):
    run = PipelineRun(
        filters={
            "city": request.city,
            "sector": request.sector,
            "max_companies": request.max_companies,
            "resume_text": request.resume_text,
        },
        status="pending",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Import here to avoid circular import at module load; enqueue ARQ job
    from app.tasks.queue import enqueue_pipeline
    await enqueue_pipeline(str(run.id), request.model_dump())

    return PipelineRunResponse(pipeline_run_id=run.id, status=run.status)


@router.get("/{run_id}/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PipelineRun).where(PipelineRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run
