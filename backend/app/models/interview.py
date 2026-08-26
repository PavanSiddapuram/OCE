import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mode: Mapped[str] = mapped_column(String, nullable=False)  # dsa, pressure_coding, lld, hld, ai_systems, research_reasoning
    title: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str] = mapped_column(String, default="medium")  # easy, medium, hard, frontier
    skill_ids: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    prompt_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_role: Mapped[str] = mapped_column(String, default="Google DeepMind Research Engineer")
    mode: Mapped[str] = mapped_column(String, nullable=False)  # dsa, pressure_coding, lld, hld, ai_systems
    difficulty: Mapped[str] = mapped_column(String, default="medium")
    status: Mapped[str] = mapped_column(String, default="active")  # active | completed | debriefed
    transcript_json: Mapped[list[dict] | None] = mapped_column(JSONB, default=list)
    scorecard_json: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    attempts: Mapped[list["InterviewAttempt"]] = relationship("InterviewAttempt", back_populates="session", cascade="all, delete-orphan")


class InterviewAttempt(Base):
    __tablename__ = "interview_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    code_response: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(String)  # pass | partial | fail
    hints_count: Mapped[int] = mapped_column(Integer, default=0)
    metrics_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["InterviewSession"] = relationship("InterviewSession", back_populates="attempts")
    question: Mapped["Question | None"] = relationship("Question")
