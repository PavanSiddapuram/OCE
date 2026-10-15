import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HiringRun(Base):
    __tablename__ = "hiring_runs"
    __table_args__ = (
        UniqueConstraint("run_date", name="uq_hiring_runs_run_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    candidates_seen: Mapped[int] = mapped_column(default=0, nullable=False)
    candidates_qualified: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HiringProspect(Base):
    __tablename__ = "hiring_prospects"
    __table_args__ = (
        UniqueConstraint("canonical_job_url", name="uq_hiring_prospects_canonical_job_url"),
        Index("ix_hiring_prospects_status_score", "status", "total_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_domain: Mapped[str | None] = mapped_column(String(255), index=True)
    company_website: Mapped[str | None] = mapped_column(Text)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_job_url: Mapped[str] = mapped_column(Text, nullable=False)
    role_location: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_verified_on: Mapped[date] = mapped_column(Date, nullable=False)
    direct_job_listing: Mapped[bool] = mapped_column(default=True, nullable=False)
    expansion_signal: Mapped[bool] = mapped_column(default=False, nullable=False)
    technical_fit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    hiring_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    contact_relevance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    score_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    qualification_reasons: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255))
    contact_role: Mapped[str | None] = mapped_column(String(255))
    contact_profile_url: Mapped[str | None] = mapped_column(Text)
    contact_email: Mapped[str | None] = mapped_column(String(320))
    status: Mapped[str] = mapped_column(String(32), default="discovered", nullable=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
