from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class HiringCandidateIn(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    company_website: HttpUrl | None = None
    role_title: str = Field(min_length=1, max_length=255)
    job_url: HttpUrl
    role_location: str = Field(min_length=1, max_length=255)
    source_type: Literal["official_careers", "company_blog", "verified_job_board", "other"]
    evidence_verified_on: date
    direct_job_listing: bool = True
    expansion_signal: bool = False
    technical_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    contact_relevance: float = Field(default=0.0, ge=0.0, le=1.0)


class HiringDryRunRequest(BaseModel):
    candidates: list[HiringCandidateIn] = Field(min_length=1, max_length=100)
    target_location: str = Field(default="Bengaluru", min_length=1, max_length=100)
    max_evidence_age_days: int = Field(default=45, ge=1, le=365)
    as_of_date: date | None = None


class HiringDryRunItem(BaseModel):
    company_name: str
    role_title: str
    job_url: str
    qualifies: bool
    reasons: list[str]
    evidence_age_days: int
    hiring_score: float
    total_score: float
    score_breakdown: dict[str, float]


class HiringDryRunResponse(BaseModel):
    mode: Literal["dry_run"] = "dry_run"
    persisted: Literal[False] = False
    candidates_seen: int
    candidates_qualified: int
    results: list[HiringDryRunItem]
    model_config = ConfigDict(extra="forbid")
