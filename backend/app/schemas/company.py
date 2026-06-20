import uuid
from datetime import datetime

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    website: str | None = None
    description: str | None = None
    sector: str | None = None
    city: str | None = None
    stage: str | None = None
    source: str | None = None
    source_url: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    mission: str | None = None
    product_summary: str | None = None
    recent_launches: list[str] | None = None
    tech_stack: list[str] | None = None
    current_focus: str | None = None
    status: str | None = None


class CompanyOut(CompanyBase):
    id: uuid.UUID
    mission: str | None = None
    product_summary: str | None = None
    recent_launches: list[str] | None = None
    tech_stack: list[str] | None = None
    current_focus: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyDetail(CompanyOut):
    opportunities: list = []
    founders: list = []
    outreach: list = []
    contacts: list = []
