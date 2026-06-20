import uuid
from datetime import datetime

from pydantic import BaseModel


class ContactCreate(BaseModel):
    company_id: uuid.UUID
    founder_id: uuid.UUID | None = None
    name: str
    email: str | None = None
    linkedin_url: str | None = None
    role: str | None = None
    contact_type: str | None = None
    notes: str | None = None


class ContactStatusUpdate(BaseModel):
    status: str


class ContactOut(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    founder_id: uuid.UUID | None = None
    name: str
    email: str | None = None
    linkedin_url: str | None = None
    role: str | None = None
    contact_type: str | None = None
    status: str
    notes: str | None = None
    last_contacted: datetime | None = None
    next_followup: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
