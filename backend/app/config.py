from pathlib import Path

from pydantic_settings import BaseSettings

# .env lives at the repo root (one level above backend/); anchor it to this
# file's location so it loads no matter which directory the app starts from
_REPO_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://oce:oce_dev@localhost:5432/oce"
    redis_url: str = "redis://localhost:6379"

    # DeepSeek — sole LLM provider for all 8 agents
    # Valid API model names: "deepseek-v4-flash" (fast/cheap) or "deepseek-v4-pro"
    # (higher quality). Override via DEEPSEEK_MODEL in .env.
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com"

    # External tools
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""

    max_companies_per_run: int = 20
    top_opportunities_for_pow: int = 5

    model_config = {"env_file": (_REPO_ROOT_ENV, ".env"), "extra": "ignore"}


settings = Settings()
