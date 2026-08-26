from pydantic import BaseModel, Field
from app.agents.base import make_agent, run_agent_with_retry


class PriorityOutcome(BaseModel):
    title: str = Field(description="Actionable must-win outcome for the week")
    track: str = Field(description="Track A (Interview) | Track B (Research) | Shared")
    target_metric: str = Field(description="Measurable exit condition (e.g. score >= 85 on 3D geometry mock, complete ablation benchmark)")
    estimated_hours: float = Field(description="Allocated time budget")


class WeeklyPlanOutput(BaseModel):
    week_start: str = Field(description="YYYY-MM-DD")
    focus_narrative: str = Field(description="Central theme or thesis for the week")
    priorities: list[PriorityOutcome] = Field(description="EXACTLY 1 to 3 must-win outcomes")
    track_a_sessions_quota: int = Field(description="Min mock interview sessions", default=5)
    track_b_experiments_quota: int = Field(description="Min experiment runs / paper analyses", default=2)
    daily_allocation_mins: int = Field(description="Daily focus block budget (60-90 min)", default=90)


SYSTEM_PROMPT = """You are the Weekly Coordinator for FRONTIER OS.
Your objective is to act as the control plane for the candidate's human schedule.
Enforce the rule: "Do less to accomplish more."

Algorithm constraints:
- Priority = (Impact * Weakness_Reduction * Evidence_Value * Urgency) / Effort
- EXACTLY 1 to 3 "must-win" outcomes per week (Never more than 3).
- Balance Track A (Interview Readiness: DSA, LLD, HLD, Pressure coding, AI systems) and Track B (Research Identity: 3D geometry, WebGPU, spatial AI).
- Allocate 60-90 mins/day.
- If an existing experiment has an unresolved result, DO NOT start a new major project.
"""

_agent = make_agent(SYSTEM_PROMPT, WeeklyPlanOutput)


async def run_weekly_coordinator(candidate_state_summary: str, week_start: str) -> WeeklyPlanOutput:
    prompt = f"Week Start: {week_start}\nCandidate State & Recent Audit Log:\n{candidate_state_summary}\n\nGenerate the 7-day Weekly Plan."
    res = await run_agent_with_retry(_agent, prompt)
    return res.data
