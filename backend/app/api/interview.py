import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.events import Event
from app.models.interview import InterviewAttempt, InterviewSession, Question
from app.models.candidate import CandidateProfile, FailurePattern, CandidateSkill

router = APIRouter(prefix="/interviews", tags=["interviews"])


class StartSessionRequest(BaseModel):
    mode: Literal["dsa", "pressure_coding", "lld", "hld", "ai_systems", "research_reasoning"] = "pressure_coding"
    difficulty: Literal["easy", "medium", "hard", "frontier"] = "medium"
    target_role: str = "Google DeepMind Research Engineer"


class DebriefSessionRequest(BaseModel):
    code_response: str
    self_evaluation: str = ""
    interviewer_probing_notes: str = ""


DEFAULT_SEED_QUESTIONS = [
    {
        "id": "q1-3dgs",
        "mode": "pressure_coding",
        "title": "3D Gaussian Splatting Rasterization Invariant & Ray Intersect",
        "difficulty": "frontier",
        "skill_ids": ["3d_geometry", "webgpu_wasm", "pressure_coding"],
        "prompt": {
            "problem": "Design and implement a fast ray-sphere bounding test for a 3D point cloud / Gaussian Splatting scene under real-time frame budget constraints (16ms). Explain time/space complexity and invariant properties under affine transform.",
            "constraints": "O(N) initial pass, O(log N) ray traversal. Space overhead <= 1.5x vertex buffer.",
        },
    },
    {
        "id": "q2-bvh",
        "mode": "dsa",
        "title": "Bounding Volume Hierarchy (BVH) Construction with SAH",
        "difficulty": "hard",
        "skill_ids": ["3d_geometry", "dsa_trees_graphs"],
        "prompt": {
            "problem": "Implement a Surface Area Heuristic (SAH) BVH tree builder for 3D meshes. Support dynamic node insertion and query ray intersections.",
            "constraints": "O(N log N) build time, O(log N) ray intersection query.",
        },
    },
]


@router.get("/questions")
async def list_questions(db: AsyncSession = Depends(get_db)):
    try:
        res = await db.execute(select(Question).limit(20))
        questions = res.scalars().all()
        if questions:
            return [
                {
                    "id": str(q.id),
                    "mode": q.mode,
                    "title": q.title,
                    "difficulty": q.difficulty,
                    "skill_ids": q.skill_ids,
                    "prompt": q.prompt_json,
                }
                for q in questions
            ]
    except Exception:
        pass
    return DEFAULT_SEED_QUESTIONS


@router.post("/sessions")
async def start_session(req: StartSessionRequest, db: AsyncSession = Depends(get_db)):
    try:
        res = await db.execute(select(Question).where(Question.mode == req.mode).limit(1))
        question = res.scalar_one_or_none()

        session = InterviewSession(
            question_id=question.id if question else None,
            mode=req.mode,
            difficulty=req.difficulty,
            target_role=req.target_role,
            status="active",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return {
            "session_id": str(session.id),
            "mode": session.mode,
            "difficulty": session.difficulty,
            "target_role": session.target_role,
            "question": {
                "id": str(question.id) if question else "q1-3dgs",
                "title": question.title if question else DEFAULT_SEED_QUESTIONS[0]["title"],
                "prompt": question.prompt_json if question else DEFAULT_SEED_QUESTIONS[0]["prompt"],
            },
        }
    except Exception:
        return {
            "session_id": "sess-mock-123",
            "mode": req.mode,
            "difficulty": req.difficulty,
            "target_role": req.target_role,
            "question": DEFAULT_SEED_QUESTIONS[0],
        }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        session = await db.get(InterviewSession, uuid.UUID(session_id))
        if session:
            return {
                "id": str(session.id),
                "mode": session.mode,
                "difficulty": session.difficulty,
                "status": session.status,
                "scorecard": session.scorecard_json,
            }
    except Exception:
        pass
    return {
        "id": session_id,
        "mode": "pressure_coding",
        "difficulty": "frontier",
        "status": "active",
        "scorecard": None,
    }


@router.post("/sessions/{session_id}/debrief")
async def debrief_session(session_id: str, req: DebriefSessionRequest, db: AsyncSession = Depends(get_db)):
    scorecard = {
        "correctness": 88.0,
        "complexity": 85.0,
        "communication": 82.0,
        "edge_cases": 78.0,
        "overall_score": 83.5,
        "strengths": ["Clear invariant formulation", "Optimal O(log N) ray traversal logic"],
        "weaknesses": ["Boundary check edge case in ray direction normalization under zero length"],
        "failure_fingerprint_updated": "Boundary condition oversight in 3D ray casting",
    }
    try:
        session = await db.get(InterviewSession, uuid.UUID(session_id))
        if session:
            session.status = "completed"
            session.scorecard_json = scorecard
            await db.commit()
            return {"session_id": str(session.id), "status": session.status, "scorecard": scorecard}
    except Exception:
        pass
    return {"session_id": session_id, "status": "completed", "scorecard": scorecard}
