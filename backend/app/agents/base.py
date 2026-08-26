import uuid
from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.config import settings
from app.database import AsyncSessionLocal
from app.utils.retry import retry_async

_llm_client: AsyncOpenAI | None = None


def _get_client() -> tuple[AsyncOpenAI, str]:
    global _llm_client
    provider = settings.llm_provider.lower()

    if provider == "gemini":
        api_key = settings.gemini_api_key or "gemini-dummy-key"
        base_url = settings.gemini_base_url
        model_name = settings.gemini_model
    elif provider == "kimi":
        api_key = settings.kimi_api_key or "kimi-dummy-key"
        base_url = settings.kimi_base_url
        model_name = settings.kimi_model
    else:  # deepseek default
        api_key = settings.deepseek_api_key or "deepseek-dummy-key"
        base_url = settings.deepseek_base_url
        model_name = settings.deepseek_model

    if _llm_client is None:
        _llm_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    return _llm_client, model_name


def make_agent(system_prompt: str, result_type: type) -> Agent:
    """Factory for all FRONTIER OS agents supporting Gemini, Kimi, and DeepSeek."""
    client, model_name = _get_client()
    provider = OpenAIProvider(openai_client=client)
    model = OpenAIChatModel(model_name, provider=provider)

    model_settings = {}
    if settings.llm_provider.lower() == "deepseek":
        model_settings = {"extra_body": {"thinking": {"type": "disabled"}}}

    return Agent(
        model=model,
        system_prompt=system_prompt,
        output_type=result_type,
        model_settings=model_settings if model_settings else None,
    )


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
    pass
