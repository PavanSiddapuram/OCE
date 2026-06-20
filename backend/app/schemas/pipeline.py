import uuid
from datetime import datetime

from pydantic import BaseModel


class PipelineRunRequest(BaseModel):
    city: str
    sector: str
    max_companies: int = 20
    resume_text: str


class PipelineRunResponse(BaseModel):
    pipeline_run_id: uuid.UUID
    status: str


class PipelineStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    current_agent: str | None = None
    agents_done: list[str] | None = None
    total_companies: int
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
