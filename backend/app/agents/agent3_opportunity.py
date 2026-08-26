"""Agent 3: Opportunity Agent — 7-Signal Weighted Target Matcher & Opportunity Brief Generator."""
import time
import uuid
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import select

from app.agents.base import log_research, make_agent, run_agent_with_retry
from app.database import AsyncSessionLocal
from app.models.company import Company
from app.models.opportunity import Opportunity


class SignalScores(BaseModel):
    technical_fit: float = Field(description="30% weight - How directly candidate's demonstrated skills map to problem (0-100)")
    evidence_strength: float = Field(description="20% weight - Executed code, benchmark, OSS, paper reproduction (0-100)")
    problem_relevance: float = Field(description="15% weight - Closeness to target team's active work (0-100)")
    gap_closability: float = Field(description="10% weight - Can missing skills be credibly developed in 4-8 wks (0-100)")
    relationship_access: float = Field(description="10% weight - Legitimate path to a conversation (0-100)")
    role_availability: float = Field(description="10% weight - Stated or credible opening (0-100)")
    strategic_uniqueness: float = Field(description="5% weight - Exploits unusual geometry/3D/WebGPU/systems combo (0-100)")

    @property
    def composite_score(self) -> float:
        return (
            0.30 * self.technical_fit +
            0.20 * self.evidence_strength +
            0.15 * self.problem_relevance +
            0.10 * self.gap_closability +
            0.10 * self.relationship_access +
            0.10 * self.role_availability +
            0.05 * self.strategic_uniqueness
        )


class OpportunityBriefSchema(BaseModel):
    problem: str = Field(description="Specific technical problem target team is solving")
    why_now: str = Field(description="Research / product / hiring signal context")
    why_you: str = Field(description="Evidence-backed candidate fit narrative")
    missing_proof: list[str] = Field(description="1 or 2 specific capability gaps to close")
    build_next: str = Field(description="Small artifact / experiment / OSS contribution idea")
    relevant_people: list[str] = Field(description="3-5 relevant researchers/engineers in this domain")
    conversation_angle: str = Field(description="Technical question or observation angle (no generic referral ask)")
    role_paths: list[str] = Field(description="Current or future potential roles")
    confidence: float = Field(description="Overall confidence rating 0.0 to 1.0")


class FrontierOpportunityOutput(BaseModel):
    target_name: str
    target_type: Literal["research_team", "role", "company", "person"]
    title: str
    category: str
    signals: SignalScores
    brief: OpportunityBriefSchema
    skills_required: list[str]


SYSTEM_PROMPT = """You are the Opportunity Agent for FRONTIER OS.
Your primary question is NOT "who can refer me?", but "which current problem is unusually aligned with evidence Pavan has produced, and who is closest to that problem?"

Evaluate target opportunities (e.g. Google DeepMind SIMA 2, Gemini Robotics, Spatial AI, 3D WebGPU, High-Growth AI Startups) against candidate evidence (3D computational geometry, CAD, WebGPU, systems, AI/ML).

Calculate the 7-signal composite fit score and generate a complete Opportunity Brief as defined in FRONTIER OS specifications.
"""

_agent = make_agent(SYSTEM_PROMPT, FrontierOpportunityOutput)


async def run_opportunity_analysis(target_input: str, candidate_evidence_summary: str = "") -> FrontierOpportunityOutput:
    prompt = f"""Target Input: {target_input}
Candidate Evidence & Skill State:
{candidate_evidence_summary}

Perform 7-signal weighted scoring and generate a complete Opportunity Brief."""
    res = await run_agent_with_retry(_agent, prompt)
    return res.data
