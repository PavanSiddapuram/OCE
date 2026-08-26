import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.events import Event
from app.models.weekly import WeeklyPlan

router = APIRouter(prefix="/weekly", tags=["weekly"])


class GenerateWeeklyPlanRequest(BaseModel):
    week_start: str = ""  # YYYY-MM-DD


DEFAULT_WEEKLY_PLAN = {
    "id": "plan-seed-001",
    "week_start": "2026-08-23",
    "priorities": [
        {
            "title": "Master 3D Ray-Sphere & BVH Tree Invariants (Track A)",
            "track": "Track A (Interview)",
            "target_metric": "Achieve score >= 85 on pressure coding mock without boundary errors",
            "estimated_hours": 6.0,
        },
        {
            "title": "Run WebGPU Bitonic Sort Ablation Benchmark (Track B)",
            "track": "Track B (Research)",
            "target_metric": "Publish benchmark comparison table: CPU Radix vs WebGPU Bitonic compute shader",
            "estimated_hours": 8.0,
        },
        {
            "title": "Generate 7-Signal Opportunity Brief for DeepMind SIMA 2 Team",
            "track": "Shared",
            "target_metric": "Finalize outreach context brief and technical paper observation",
            "estimated_hours": 3.0,
        },
    ],
    "time_budget": {
        "daily_mins": 90,
        "track_a_mins_day": 45,
        "track_b_mins_day": 45,
    },
    "track_a_quota": 5,
    "track_b_quota": 2,
    "status": "active",
    "created_at": "2026-08-23T00:00:00Z",
}


@router.get("/plan")
async def get_current_weekly_plan(db: AsyncSession = Depends(get_db)):
    try:
        res = await db.execute(select(WeeklyPlan).order_by(WeeklyPlan.created_at.desc()).limit(1))
        plan = res.scalar_one_or_none()

        if plan:
            return {
                "id": str(plan.id),
                "week_start": plan.week_start,
                "priorities": plan.priorities_json,
                "time_budget": plan.time_budget_json,
                "track_a_quota": plan.track_a_quota,
                "track_b_quota": plan.track_b_quota,
                "status": plan.status,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
            }
    except Exception:
        pass
    return DEFAULT_WEEKLY_PLAN


@router.post("/plan")
async def generate_weekly_plan(req: GenerateWeeklyPlanRequest, db: AsyncSession = Depends(get_db)):
    try:
        today = datetime.utcnow()
        week_start_str = req.week_start or today.strftime("%Y-%m-%d")

        plan = WeeklyPlan(
            week_start=week_start_str,
            priorities_json=DEFAULT_WEEKLY_PLAN["priorities"],
            time_budget_json=DEFAULT_WEEKLY_PLAN["time_budget"],
            track_a_quota=5,
            track_b_quota=2,
            status="active",
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        return {
            "id": str(plan.id),
            "week_start": plan.week_start,
            "priorities": plan.priorities_json,
            "time_budget": plan.time_budget_json,
            "track_a_quota": plan.track_a_quota,
            "track_b_quota": plan.track_b_quota,
            "status": plan.status,
        }
    except Exception:
        return DEFAULT_WEEKLY_PLAN
