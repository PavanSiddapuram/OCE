import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Float, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, default="Pavan Siddapuram")
    target_trajectory: Mapped[str] = mapped_column(String, default="Google SWE / AI-ML / DeepMind Research Engineer")
    geography: Mapped[str] = mapped_column(String, default="Bengaluru / Global")
    identity_json: Mapped[dict | None] = mapped_column(JSONB)
    constraints_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    skills: Mapped[list["CandidateSkill"]] = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    failure_patterns: Mapped[list["FailurePattern"]] = relationship("FailurePattern", back_populates="candidate", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # e.g., "3d_geometry", "webgpu", "dsa_trees"
    name: Mapped[str] = mapped_column(String, nullable=False)
    domain: Mapped[str] = mapped_column(String, nullable=False)  # track_a | track_b | shared
    parent_id: Mapped[str | None] = mapped_column(String, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=50)  # 0 to 100
    confidence: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 to 1.0
    evidence_ids: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    candidate: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="skills")


class FailurePattern(Base):
    __tablename__ = "failure_patterns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    domain: Mapped[str] = mapped_column(String, nullable=False)  # dsa, pressure_coding, lld, hld, math, reasoning
    pattern: Mapped[str] = mapped_column(String, nullable=False)  # e.g. "Boundary condition oversight in 3D ray casting"
    count: Mapped[int] = mapped_column(Integer, default=1)
    severity: Mapped[str] = mapped_column(String, default="medium")  # low | medium | high | critical
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    candidate: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="failure_patterns")
