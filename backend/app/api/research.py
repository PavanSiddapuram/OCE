import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.gemini_deep_research import gemini_deep_research
from app.database import get_db
from app.models.events import Event
from app.models.evidence import EvidenceItem
from app.models.frontier_research import ExperimentRun, ResearchProject

router = APIRouter(prefix="/research", tags=["research"])


class CreateProjectRequest(BaseModel):
    title: str
    question: str
    hypothesis: str
    repo_url: str = ""
    tags: list[str] = ["3d_geometry", "webgpu", "spatial_ai"]


class LogExperimentRequest(BaseModel):
    project_id: str
    commit_sha: str = "main"
    dataset: str = "Synthetic 3D Scene / ModelNet40"
    config: dict = {}
    metrics: dict = {"fps": 60, "psnr": 32.5, "vram_mb": 1200}
    result_summary: str = "Baseline rasterizer achieved 60 FPS under 100k points."


class StartDeepResearchRequest(BaseModel):
    prompt: str
    agent: str = "deep-research-preview-04-2026"  # deep-research-preview-04-2026 or deep-research-max-preview-04-2026
    collaborative_planning: bool = False
    visualization: str = "auto"
    use_alphaxiv_mcp: bool = True


class RefineDeepResearchRequest(BaseModel):
    prompt: str
    approve_plan: bool = False
    collaborative_planning: bool = True


@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ResearchProject).order_by(ResearchProject.created_at.desc()))
    projects = res.scalars().all()
    if not projects:
        p1 = ResearchProject(
            title="WebGPU 3D Gaussian Splatting Rasterizer Baseline",
            question="Can a pure WebGPU compute shader rasterizer render 500k 3D Gaussians at 60 FPS in browser with under 2GB VRAM?",
            hypothesis="Using tiled tile-based sorting in WebGPU compute shaders will eliminate CPU sorting bottlenecks and achieve 60+ FPS.",
            stage="experiment",
            repo_url="https://github.com/PavanSiddapuram/webgpu-3dgs-rasterizer",
            next_action="Run ablation benchmark comparing CPU radix sort vs compute shader bitonic sort.",
            tags=["3d_geometry", "webgpu_wasm", "spatial_ai"],
        )
        db.add(p1)
        await db.commit()
        res = await db.execute(select(ResearchProject).order_by(ResearchProject.created_at.desc()))
        projects = res.scalars().all()

    return [
        {
            "id": str(p.id),
            "title": p.title,
            "question": p.question,
            "hypothesis": p.hypothesis,
            "stage": p.stage,
            "repo_url": p.repo_url,
            "next_action": p.next_action,
            "tags": p.tags,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in projects
    ]


@router.post("/projects")
async def create_project(req: CreateProjectRequest, db: AsyncSession = Depends(get_db)):
    project = ResearchProject(
        title=req.title,
        question=req.question,
        hypothesis=req.hypothesis,
        repo_url=req.repo_url,
        tags=req.tags,
        stage="discovery",
        next_action="Setup baseline environment and code repository structure.",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    event = Event(
        event_type="research.project.created",
        actor="user",
        entity_ref=f"research_project:{project.id}",
        payload_json={"title": project.title, "question": project.question},
    )
    db.add(event)
    await db.commit()

    return {"id": str(project.id), "title": project.title, "stage": project.stage}


@router.post("/experiments")
async def log_experiment(req: LogExperimentRequest, db: AsyncSession = Depends(get_db)):
    project = await db.get(ResearchProject, uuid.UUID(req.project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    exp = ExperimentRun(
        project_id=project.id,
        commit_sha=req.commit_sha,
        dataset=req.dataset,
        config_json=req.config,
        metrics_json=req.metrics,
        result_summary=req.result_summary,
        status="completed",
    )
    db.add(exp)

    evidence = EvidenceItem(
        type="benchmark",
        source_url=project.repo_url or "https://github.com/PavanSiddapuram",
        source_type="official",
        claim=f"Completed experiment on '{project.title}': {req.result_summary}",
        confidence=0.9,
        supports=project.tags,
        artifact_url=project.repo_url,
        provenance_notes=f"Commit SHA: {req.commit_sha}, Metrics: {req.metrics}",
    )
    db.add(evidence)

    event = Event(
        event_type="experiment.completed",
        actor="system",
        entity_ref=f"experiment:{exp.id}",
        payload_json={"project_id": str(project.id), "metrics": req.metrics},
    )
    db.add(event)

    await db.commit()
    return {"id": str(exp.id), "project_id": str(project.id), "status": exp.status, "metrics": req.metrics}


# --- Gemini Deep Research Agent (Interactions API) Endpoints ---

@router.post("/deep-research/start")
async def start_deep_research(req: StartDeepResearchRequest, db: AsyncSession = Depends(get_db)):
    """Start an autonomous Gemini Deep Research task in the background."""
    res = await gemini_deep_research.create_research_interaction(
        prompt=req.prompt,
        agent=req.agent,
        collaborative_planning=req.collaborative_planning,
        visualization=req.visualization,
        use_alphaxiv_mcp=req.use_alphaxiv_mcp,
    )

    interaction_id = res.get("interaction", {}).get("id") or res.get("id") or "deep-res-mock-9988"

    event = Event(
        event_type="gemini.deep_research.started",
        actor="agent",
        entity_ref=f"deep_research:{interaction_id}",
        payload_json={"prompt": req.prompt, "agent": req.agent, "collaborative_planning": req.collaborative_planning},
    )
    db.add(event)
    await db.commit()

    return {"interaction_id": interaction_id, "status": res.get("status", "in_progress"), "raw": res}


@router.get("/deep-research/{interaction_id}")
async def get_deep_research_status(interaction_id: str):
    """Poll Gemini Deep Research interaction status, reasoning steps, reports & charts."""
    res = await gemini_deep_research.get_interaction_status(interaction_id)
    return res


@router.post("/deep-research/{interaction_id}/refine")
async def refine_deep_research_plan(
    interaction_id: str, req: RefineDeepResearchRequest, db: AsyncSession = Depends(get_db)
):
    """Refine or approve a collaborative research plan using previous_interaction_id."""
    res = await gemini_deep_research.create_research_interaction(
        prompt=req.prompt,
        collaborative_planning=not req.approve_plan,
        previous_interaction_id=interaction_id,
    )
    return res
