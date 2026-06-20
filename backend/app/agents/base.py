import os
import uuid

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from app.config import settings
from app.database import AsyncSessionLocal


def make_agent(system_prompt: str, result_type: type) -> Agent:
    """Factory for all OCE agents — single model config point."""
    # pydantic-ai's anthropic provider reads ANTHROPIC_API_KEY from env
    os.environ.setdefault("ANTHROPIC_API_KEY", settings.anthropic_api_key)
    model = AnthropicModel(settings.anthropic_model)
    return Agent(model=model, system_prompt=system_prompt, output_type=result_type)


async def log_research(
    company_id: str,
    agent_name: str,
    raw_input: dict,
    raw_output: dict,
    tokens_used: int | None = None,
    duration_ms: int | None = None,
):
    """Persist every agent run to the research table for audit and barrier checks."""
    from app.models.research import Research

    async with AsyncSessionLocal() as db:
        entry = Research(
            id=uuid.uuid4(),
            company_id=company_id,
            agent_name=agent_name,
            raw_input=raw_input,
            raw_output=raw_output,
            tokens_used=tokens_used,
            model_used=settings.anthropic_model,
            duration_ms=duration_ms,
        )
        db.add(entry)
        await db.commit()
