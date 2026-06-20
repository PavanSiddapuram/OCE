"""Agent 8: CRM Updater — ensures contacts exist and sets initial CRM state."""
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.company import Company
from app.models.contact import Contact
from app.models.founder import Founder


async def run_crm_update(company_id: str) -> None:
    async with AsyncSessionLocal() as db:
        # Load company with founders
        company_result = await db.execute(
            select(Company)
            .options(selectinload(Company.founders), selectinload(Company.contacts))
            .where(Company.id == company_id)
        )
        company = company_result.scalar_one_or_none()
        if not company:
            return

        existing_contact_names = {c.name for c in company.contacts}

        for founder in company.founders:
            if founder.name not in existing_contact_names:
                contact = Contact(
                    id=uuid.uuid4(),
                    company_id=company_id,
                    founder_id=founder.id,
                    name=founder.name,
                    linkedin_url=founder.linkedin_url,
                    role=founder.role or "Founder",
                    contact_type="Founder",
                    status="not_contacted",
                    next_followup=datetime.utcnow() + timedelta(days=7),
                )
                db.add(contact)

        await db.commit()
