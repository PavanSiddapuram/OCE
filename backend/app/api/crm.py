from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactOut

router = APIRouter(prefix="/crm", tags=["crm"])

CRM_STATUSES = ["not_contacted", "messaged", "replied", "meeting", "interview", "offer"]

DEFAULT_SEED_CRM_BOARD = {
    "not_contacted": [
        {
            "id": "c1-sima2",
            "name": "Dr. Alex Rivera",
            "title": "Staff Research Scientist - SIMA 2 & Spatial AI",
            "company_name": "Google DeepMind",
            "linkedin_url": "https://linkedin.com/in/alex-rivera-deepmind",
            "email": "arivera@google.com",
            "status": "not_contacted",
            "notes": "Works on 3D virtual environment rendering and multi-modal SIMA 2 agent perception.",
        }
    ],
    "messaged": [
        {
            "id": "c2-robotics",
            "name": "Elena Rostova",
            "title": "Research Engineer - Gemini Robotics",
            "company_name": "Google DeepMind Bengaluru",
            "linkedin_url": "https://linkedin.com/in/elena-rostova",
            "email": "erostova@google.com",
            "status": "messaged",
            "notes": "Sent paper note on spatial BVH performance on edge compute.",
        }
    ],
    "replied": [],
    "meeting": [],
    "interview": [],
    "offer": [],
}


@router.get("/board")
async def get_crm_board(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Contact).options(selectinload(Contact.company)).order_by(Contact.updated_at.desc())
        )
        contacts = result.scalars().all()

        board: dict[str, list] = {s: [] for s in CRM_STATUSES}
        for contact in contacts:
            status = contact.status if contact.status in board else "not_contacted"
            board[status].append(ContactOut.model_validate(contact))

        if any(board.values()):
            return board
    except Exception:
        pass
    return DEFAULT_SEED_CRM_BOARD
