import uuid

from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.config import settings
from app.database import AsyncSessionLocal
from app.utils.retry import retry_async

# Single shared async client — DeepSeek is OpenAI-API-compatible
_openai_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _openai_client


def make_agent(system_prompt: str, result_type: type) -> Agent:
    """Factory for all OCE agents — DeepSeek via OpenAI-compatible provider."""
    provider = OpenAIProvider(openai_client=_get_client())
    model = OpenAIChatModel(settings.deepseek_model, provider=provider)
    return Agent(model=model, system_prompt=system_prompt, output_type=result_type)


async def run_agent_with_retry(agent: Agent, prompt: str, retries: int = 3, base_delay: float = 10.0):
    """Run a pydantic-ai agent with exponential backoff for transient API errors."""
    return await retry_async(
        agent.run,
        prompt,
        retries=retries,
        base_delay=base_delay,
        max_delay=60.0,
        exceptions=(Exception,),
    )


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
            model_used=settings.deepseek_model,
            duration_ms=duration_ms,
        )
        db.add(entry)
        await db.commit()
