import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    founder_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("founders.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String)
    linkedin_url: Mapped[str | None] = mapped_column(String)
    role: Mapped[str | None] = mapped_column(String)
    contact_type: Mapped[str | None] = mapped_column(String)  # Founder | Recruiter | Employee | Referral
    status: Mapped[str] = mapped_column(String, default="not_contacted")
    notes: Mapped[str | None] = mapped_column(Text)
    last_contacted: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_followup: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="contacts")
    founder: Mapped["Founder | None"] = relationship("Founder", back_populates="contacts")
    outreach: Mapped[list["Outreach"]] = relationship("Outreach", back_populates="contact")
