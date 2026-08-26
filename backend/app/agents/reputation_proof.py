from pydantic import BaseModel, Field
from app.agents.base import make_agent, run_agent_with_retry


class PublicProofOutput(BaseModel):
    artifact_type: str = Field(description="github_readme | technical_note | benchmark_report | oss_pr_proposal")
    title: str
    headline: str
    key_findings: list[str]
    formatted_markdown: str = Field(description="Complete ready-to-publish markdown artifact")
    oss_contribution_angle: str = Field(description="How to upstream or share this with the community")


SYSTEM_PROMPT = """You are the Reputation / Proof Agent for FRONTIER OS.
Your objective is to convert completed technical experiments, code implementations, and benchmark results into high-signal public evidence.

Standards for public proof:
- What was the problem?
- What did I actually build?
- What did I measure (metrics, baselines, hardware specs)?
- What failed or didn't work?
- What changed / conclusion?

Never create generic marketing fluff or generic tutorial framing. Emphasize rigorous engineering evidence.
"""

_agent = make_agent(SYSTEM_PROMPT, PublicProofOutput)


async def run_reputation_proof(experiment_data_summary: str) -> PublicProofOutput:
    prompt = f"Experiment / Code Summary:\n{experiment_data_summary}\n\nFormat into a credible public proof artifact."
    res = await run_agent_with_retry(_agent, prompt)
    return res.data
