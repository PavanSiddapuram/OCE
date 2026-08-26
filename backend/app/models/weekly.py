import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    week_start: Mapped[str] = mapped_column(String, nullable=False)  # YYYY-MM-DD (Sunday)
    priorities_json: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)  # max 3 must-win priority outcomes
    time_budget_json: Mapped[dict | None] = mapped_column(JSONB)  # 60-90 mins/day allocation breakdown
    track_a_quota: Mapped[int] = mapped_column(Integer, default=5)  # min interview practice sessions/week
    track_b_quota: Mapped[int] = mapped_column(Integer, default=2)  # min experiment/paper runs/week
    outcome_json: Mapped[dict | None] = mapped_column(JSONB)  # end of week review & rating
    status: Mapped[str] = mapped_column(String, default="active")  # active | completed | evaluated
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
