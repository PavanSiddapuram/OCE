import uuid
from datetime import datetime

from pydantic import BaseModel


class OpportunityOut(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    category: str | None = None
    description: str | None = None
    impact: str | None = None
    fit_score: int | None = None
    fit_reasoning: str | None = None
    pow_idea: str | None = None
    pow_repo_url: str | None = None
    skills_required: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
