from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.candidate import CandidateProfile, CandidateSkill, FailurePattern, Skill
from app.models.events import Event
from app.models.weekly import WeeklyPlan

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/state")
async def get_candidate_state(db: AsyncSession = Depends(get_db)):
    """Fetch unified Candidate State summary (Skills, Failures, Current Weekly Plan, Recent Events)."""
    try:
        # 1. Candidate Profile
        prof_res = await db.execute(select(CandidateProfile).limit(1))
        profile = prof_res.scalar_one_or_none()
        
        if not profile:
            profile = CandidateProfile(
                name="Pavan Siddapuram",
                target_trajectory="Google SWE / AI-ML / DeepMind Research Engineer",
                geography="Bengaluru / Global",
                identity_json={
                    "core_edge": "Computational Geometry + 3D/CAD + WebGPU/WASM + Manufacturing + AI/ML Systems",
                    "horizon": "August 2026 -> March/April 2027",
                },
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        # 2. Skills
        skills_res = await db.execute(select(CandidateSkill).where(CandidateSkill.candidate_id == profile.id))
        candidate_skills = skills_res.scalars().all()

        if not candidate_skills:
            seed_skills = [
                ("3d_geometry", "Computational Geometry & 3D", "track_b", 78, 0.8),
                ("webgpu_wasm", "WebGPU & WASM Graphics", "track_b", 82, 0.85),
                ("ai_systems", "ML Systems & PyTorch/CUDA", "track_b", 72, 0.75),
                ("dsa_trees_graphs", "DSA & Algorithms", "track_a", 75, 0.7),
                ("pressure_coding", "Coding Under Pressure", "track_a", 65, 0.6),
                ("system_design", "High Level & Distributed Systems", "track_a", 70, 0.65),
            ]
            for sk_id, name, domain, score, conf in seed_skills:
                sk_obj = await db.get(Skill, sk_id)
                if not sk_obj:
                    db.add(Skill(id=sk_id, name=name, domain=domain))
                cs = CandidateSkill(
                    candidate_id=profile.id,
                    skill_id=sk_id,
                    score=score,
                    confidence=conf,
                    evidence_ids=[],
                )
                db.add(cs)
            await db.commit()
            skills_res = await db.execute(select(CandidateSkill).where(CandidateSkill.candidate_id == profile.id))
            candidate_skills = skills_res.scalars().all()

        # 3. Failure Patterns
        fail_res = await db.execute(select(FailurePattern).where(FailurePattern.candidate_id == profile.id))
        failures = fail_res.scalars().all()

        if not failures:
            seed_fails = [
                ("dsa", "Boundary condition oversight in 3D ray casting / spatial partitions", "high", 3),
                ("pressure_coding", "Time complexity derivation under interviewer probing", "medium", 2),
            ]
            for dom, pat, sev, cnt in seed_fails:
                fp = FailurePattern(candidate_id=profile.id, domain=dom, pattern=pat, severity=sev, count=cnt)
                db.add(fp)
            await db.commit()
            fail_res = await db.execute(select(FailurePattern).where(FailurePattern.candidate_id == profile.id))
            failures = fail_res.scalars().all()

        # 4. Current Weekly Plan
        wp_res = await db.execute(select(WeeklyPlan).order_by(WeeklyPlan.created_at.desc()).limit(1))
        current_weekly_plan = wp_res.scalar_one_or_none()

        # 5. Recent Audit Events
        events_res = await db.execute(select(Event).order_by(Event.created_at.desc()).limit(10))
        recent_events = events_res.scalars().all()

        return {
            "profile": {
                "id": str(profile.id),
                "name": profile.name,
                "target_trajectory": profile.target_trajectory,
                "geography": profile.geography,
                "identity": profile.identity_json,
            },
            "skills": [
                {
                    "skill_id": cs.skill_id,
                    "score": cs.score,
                    "confidence": cs.confidence,
                    "updated_at": cs.updated_at.isoformat() if cs.updated_at else None,
                }
                for cs in candidate_skills
            ],
            "failures": [
                {
                    "id": str(f.id),
                    "domain": f.domain,
                    "pattern": f.pattern,
                    "count": f.count,
                    "severity": f.severity,
                    "last_seen": f.last_seen.isoformat() if f.last_seen else None,
                }
                for f in failures
            ],
            "weekly_plan": {
                "id": str(current_weekly_plan.id) if current_weekly_plan else None,
                "week_start": current_weekly_plan.week_start if current_weekly_plan else None,
                "priorities": current_weekly_plan.priorities_json if current_weekly_plan else [],
                "track_a_quota": current_weekly_plan.track_a_quota if current_weekly_plan else 5,
                "track_b_quota": current_weekly_plan.track_b_quota if current_weekly_plan else 2,
            } if current_weekly_plan else None,
            "recent_events": [
                {
                    "id": str(e.id),
                    "event_type": e.event_type,
                    "actor": e.actor,
                    "payload": e.payload_json,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in recent_events
            ],
        }
    except Exception:
        # Fallback candidate state when DB is offline
        return {
            "profile": {
                "id": "dev-profile-id",
                "name": "Pavan Siddapuram",
                "target_trajectory": "Google SWE / AI-ML / DeepMind Research Engineer",
                "geography": "Bengaluru / Global",
                "identity": {
                    "core_edge": "Computational Geometry + 3D/CAD + WebGPU/WASM + Manufacturing + AI/ML Systems",
                    "horizon": "August 2026 -> March/April 2027",
                },
            },
            "skills": [
                {"skill_id": "3d_geometry", "score": 78, "confidence": 0.8},
                {"skill_id": "webgpu_wasm", "score": 82, "confidence": 0.85},
                {"skill_id": "ai_systems", "score": 72, "confidence": 0.75},
                {"skill_id": "dsa_trees_graphs", "score": 75, "confidence": 0.7},
                {"skill_id": "pressure_coding", "score": 65, "confidence": 0.6},
            ],
            "failures": [
                {"id": "f1", "domain": "dsa", "pattern": "Boundary condition oversight in 3D ray casting / spatial partitions", "count": 3, "severity": "high"},
                {"id": "f2", "domain": "pressure_coding", "pattern": "Time complexity derivation under interviewer probing", "count": 2, "severity": "medium"},
            ],
            "weekly_plan": {
                "id": "dev-plan-id",
                "week_start": "2026-08-23",
                "priorities": [
                    {"title": "Master 3D Ray-Sphere & BVH Tree Invariants (Track A)", "track": "Track A (Interview)", "target_metric": "Score >= 85", "estimated_hours": 6.0},
                    {"title": "Run WebGPU Bitonic Sort Ablation Benchmark (Track B)", "track": "Track B (Research)", "target_metric": "Publish benchmark comparison", "estimated_hours": 8.0},
                    {"title": "Generate 7-Signal Opportunity Brief for DeepMind SIMA 2 Team", "track": "Shared", "target_metric": "Finalize outreach brief", "estimated_hours": 3.0},
                ],
                "track_a_quota": 5,
                "track_b_quota": 2,
            },
            "recent_events": [
                {"id": "ev1", "event_type": "candidate.state.initialized", "actor": "system", "payload": {"status": "active"}},
            ],
        }
