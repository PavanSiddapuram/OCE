from pydantic import BaseModel, Field
from app.agents.base import make_agent, run_agent_with_retry


class ResearchSignal(BaseModel):
    title: str = Field(description="Name of research paper, project, or role signal")
    source_url: str = Field(description="URL to paper, repo, or careers page")
    organization: str = Field(description="Google DeepMind | Google Research | Frontier Lab")
    core_problem: str = Field(description="Core technical problem addressed by the team")
    key_technologies: list[str] = Field(description="3DGS, NeRF, WebGPU, PyTorch, CUDA, Spatial AI, SIMA 2, etc.")
    relevance_score: float = Field(description="0.0 to 1.0 relevance to candidate edge (3D/geometry/WebGPU/systems)")
    hypothesis: str = Field(description="Proposed experiment or PoW contribution hypothesis")


class FrontierResearcherOutput(BaseModel):
    signals: list[ResearchSignal]
    summary: str


SYSTEM_PROMPT = """You are the Frontier Researcher Agent for FRONTIER OS.
Your objective is to discover and analyze frontier research directions, papers, repos, and engineering role signals from top labs (specifically Google DeepMind, Google Research, Spatial AI, SIMA 2, Gemini Robotics).

Identify specific, high-leverage technical problems aligned with the candidate's edge:
- Computational Geometry & 3D (3DGS, Mesh processing, spatial representations)
- WebGPU / WASM / High-performance graphics & ML clients
- Systems & AI/ML Systems Engineering (C++, CUDA, PyTorch, distributed training/inference)

Return structured signals with confidence ratings, source provenance, and actionable experiment hypotheses.
"""

_agent = make_agent(SYSTEM_PROMPT, FrontierResearcherOutput)


async def run_frontier_researcher(query_topic: str) -> FrontierResearcherOutput:
    prompt = f"Analyze frontier research signals and research problems for topic: {query_topic}"
    res = await run_agent_with_retry(_agent, prompt)
    return res.data
