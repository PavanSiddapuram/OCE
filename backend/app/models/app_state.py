from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AppState(Base):
    """A generic key-value store for AlgoReal's client state (DSA topic
    progress, Warmup Room completion, Interview OS sessions, the Public
    Presence OSS checklist, etc.) -- deliberately not modeled as bespoke
    relational tables per feature. This is a single-user personal app; the
    value a proper relational schema would add (querying across users,
    referential integrity between features) doesn't apply here. A key-value
    store lets AlgoReal keep the exact same keys it already uses in
    localStorage, just persisted centrally instead of per-browser."""

    __tablename__ = "app_state"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[Any] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
