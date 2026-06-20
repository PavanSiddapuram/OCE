import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Founder(Base):
    __tablename__ = "founders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str | None] = mapped_column(String)
    linkedin_url: Mapped[str | None] = mapped_column(String)
    twitter_url: Mapped[str | None] = mapped_column(String)
    personal_blog: Mapped[str | None] = mapped_column(String)
    background: Mapped[str | None] = mapped_column(Text)
    complaints: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    podcast_links: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    interview_links: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    raw_research: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="founders")
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="founder")
