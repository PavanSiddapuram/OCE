import uuid
from datetime import datetime

from pydantic import BaseModel


class OutreachOut(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    opportunity_id: uuid.UUID | None = None
    contact_id: uuid.UUID | None = None
    channel: str | None = None
    subject: str | None = None
    body: str | None = None
    hook: str | None = None
    why_company: str | None = None
    why_problem: str | None = None
    why_me: str | None = None
    what_i_built: str | None = None
    call_to_action: str | None = None
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}
