import uuid
from datetime import datetime

from pydantic import BaseModel


class FounderOut(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    role: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None
    personal_blog: str | None = None
    background: str | None = None
    complaints: list[str] | None = None
    podcast_links: list[str] | None = None
    interview_links: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
