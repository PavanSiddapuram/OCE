from pathlib import Path

from pydantic_settings import BaseSettings


# Resolve the repository-root .env independently of the caller's working directory.
# In Docker, Compose injects values through the process environment instead.
_ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://oce:oce_dev@localhost:5432/oce"
    redis_url: str = "redis://localhost:6379"

    # DeepSeek — sole LLM provider for all 8 agents
    # "deepseek-chat" is DeepSeek's always-latest alias (deepseek-chat).
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"

    # External tools
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""

    max_companies_per_run: int = 20
    top_opportunities_for_pow: int = 5

    # Comma-separated extra CORS origins for deployed frontends.
    extra_cors_origins: str = ""

    model_config = {"env_file": _ROOT_ENV_FILE, "extra": "ignore"}


settings = Settings()
