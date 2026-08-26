import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str | None] = mapped_column(String)  # e.g., Staff Research Engineer, DeepMind Robotics
    org: Mapped[str | None] = mapped_column(String)   # e.g., Google DeepMind, Google Research, YC Startup
    public_urls: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    topics_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    relationships: Mapped[list["Relationship"]] = relationship("Relationship", back_populates="person", cascade="all, delete-orphan")


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    stage: Mapped[str] = mapped_column(String, default="discovered")
    # discovered | context_ready | contacted | conversation | technical_relationship | referral_ready
    last_contact: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes_json: Mapped[dict | None] = mapped_column(JSONB)
    outreach_brief: Mapped[str | None] = mapped_column(Text)  # Context-rich conversation brief (Human approves before sending)
    next_step: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    person: Mapped["Person"] = relationship("Person", back_populates="relationships")
