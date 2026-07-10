import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String)  # bottleneck | growth_lever | missing_piece | technical_debt
    description: Mapped[str | None] = mapped_column(Text)
    impact: Mapped[str | None] = mapped_column(Text)
    fit_score: Mapped[int | None] = mapped_column(Integer)
    fit_reasoning: Mapped[str | None] = mapped_column(Text)
    pow_idea: Mapped[str | None] = mapped_column(Text)
    pow_repo_url: Mapped[str | None] = mapped_column(String)
    skills_required: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    pressure_test: Mapped[dict | None] = mapped_column(JSONB)  # agent9 verdict gate before building the PoW
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="opportunities")
    outreach: Mapped[list["Outreach"]] = relationship("Outreach", back_populates="opportunity")
