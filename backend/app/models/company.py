import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    website: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    mission: Mapped[str | None] = mapped_column(Text)
    product_summary: Mapped[str | None] = mapped_column(Text)
    recent_launches: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    tech_stack: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    current_focus: Mapped[str | None] = mapped_column(Text)
    sector: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    stage: Mapped[str | None] = mapped_column(String)
    source: Mapped[str | None] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(String)
    founded_year: Mapped[int | None] = mapped_column()
    employee_count: Mapped[str | None] = mapped_column(String)
    crunchbase_url: Mapped[str | None] = mapped_column(String)
    linkedin_url: Mapped[str | None] = mapped_column(String)
    twitter_url: Mapped[str | None] = mapped_column(String)
    raw_scrape_data: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String, default="discovered")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    founders: Mapped[list["Founder"]] = relationship("Founder", back_populates="company", cascade="all, delete-orphan")
    opportunities: Mapped[list["Opportunity"]] = relationship("Opportunity", back_populates="company", cascade="all, delete-orphan")
    research: Mapped[list["Research"]] = relationship("Research", back_populates="company", cascade="all, delete-orphan")
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    outreach: Mapped[list["Outreach"]] = relationship("Outreach", back_populates="company", cascade="all, delete-orphan")
