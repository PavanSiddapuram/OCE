from pydantic import BaseModel, Field
from app.agents.base import make_agent, run_agent_with_retry


class ExperimentSpecOutput(BaseModel):
    project_title: str
    question: str
    hypothesis: str
    baseline_setup: str = Field(description="Architecture and reference baseline")
    ablation_plan: list[str] = Field(description="Specific parameter or model variations to test")
    metrics_to_measure: list[str] = Field(description="FPS, PSNR, SSIM, VRAM usage, inference latency, loss curve")
    dataset_reqs: str = Field(description="Datasets required (e.g. Synthetic NeRF 3D scene, ModelNet40, custom CAD dataset)")
    repo_structure: str = Field(description="Suggested code directory structure")


SYSTEM_PROMPT = """You are the Builder / Experiment Agent for FRONTIER OS.
Your role is to convert research questions into tight, reproducible technical experiments.
Provide exact baseline architecture specs, ablation variables, metrics to benchmark, and dataset requirements for computational geometry, 3D vision, WebGPU, and AI systems experiments.
"""

_agent = make_agent(SYSTEM_PROMPT, ExperimentSpecOutput)


async def run_builder_experiment(research_question: str, constraints: str = "") -> ExperimentSpecOutput:
    prompt = f"Research Question: {research_question}\nConstraints: {constraints}\n\nDesign a reproducible baseline experiment spec."
    res = await run_agent_with_retry(_agent, prompt)
    return res.data
