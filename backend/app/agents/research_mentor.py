from pydantic import BaseModel, Field
from app.agents.base import make_agent, run_agent_with_retry


class LearningTask(BaseModel):
    title: str = Field(description="Actionable task title")
    description: str = Field(description="Step-by-step technical learning activity")
    domain: str = Field(description="geometry_3d | webgpu | systems_ml | interview_dsa")
    estimated_hours: float = Field(description="Estimated hours required")
    prerequisite_gaps: list[str] = Field(description="Gaps this task closes")


class LearningPathOutput(BaseModel):
    target_role: str
    overall_gap_summary: str
    learning_tasks: list[LearningTask]
    recommended_horizon_weeks: int = 4


SYSTEM_PROMPT = """You are the Research Mentor Agent for FRONTIER OS.
Your objective is to diagnose candidate skill posteriors and failure patterns against target roles (Google DeepMind Research Engineer / SWE).
Design tight, practical learning paths with measurable output goals (e.g. build a WebGPU 3D Gaussian Splatting viewer, implement a custom CUDA kernel for point cloud rasterization, or master 3D spatial transforms).

Avoid generic course recommendations. Focus on failure-driven, project-based learning tasks that produce verifiable code artifacts.
"""

_agent = make_agent(SYSTEM_PROMPT, LearningPathOutput)


async def run_research_mentor(candidate_state_summary: str, target_role: str) -> LearningPathOutput:
    prompt = f"Target Role: {target_role}\nCandidate Current State:\n{candidate_state_summary}\n\nGenerate an adaptive learning path."
    res = await run_agent_with_retry(_agent, prompt)
    return res.data
