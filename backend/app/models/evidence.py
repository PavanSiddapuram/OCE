import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String, nullable=False)  # code | benchmark | technical_note | oss_pr | research_note | paper_read
    source_url: Mapped[str | None] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String, default="official")  # official | employee | candidate | community
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.8)  # 0.0 to 1.0
    supports: Mapped[list[str] | None] = mapped_column(ARRAY(Text))  # skill IDs or team IDs
    contradicts: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    artifact_url: Mapped[str | None] = mapped_column(String)
    provenance_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
