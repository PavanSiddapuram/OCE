import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    target_type: Mapped[str] = mapped_column(String, default="research_team")  # research_team | role | company | person
    target_name: Mapped[str | None] = mapped_column(String)  # e.g., "Google DeepMind SIMA 2 / Spatial AI"
    category: Mapped[str | None] = mapped_column(String)  # bottleneck | growth_lever | missing_piece | technical_debt | research_frontier
    description: Mapped[str | None] = mapped_column(Text)
    impact: Mapped[str | None] = mapped_column(Text)
    fit_score: Mapped[int | None] = mapped_column(Integer)  # 0 to 100
    fit_reasoning: Mapped[str | None] = mapped_column(Text)
    signal_scores_json: Mapped[dict | None] = mapped_column(JSONB)  # 7 weighted signals breakdown
    brief_json: Mapped[dict | None] = mapped_column(JSONB)  # Complete Opportunity Brief
    pow_idea: Mapped[str | None] = mapped_column(Text)
    pow_repo_url: Mapped[str | None] = mapped_column(String)
    skills_required: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    pressure_test: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String, default="surfaced")  # surfaced | approved | snoozed | archived
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company | None"] = relationship("Company", back_populates="opportunities")
    outreach: Mapped[list["Outreach"]] = relationship("Outreach", back_populates="opportunity")
