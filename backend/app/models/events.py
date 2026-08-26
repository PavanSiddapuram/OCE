import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String, nullable=False)  # e.g., interview.failure.detected, experiment.completed
    actor: Mapped[str] = mapped_column(String, default="agent")  # user | agent | system
    entity_ref: Mapped[str | None] = mapped_column(String)  # e.g. "skill:3d_geometry" or "project:uuid"
    confidence: Mapped[float | None] = mapped_column(Float)
    payload_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
