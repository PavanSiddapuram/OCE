from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://oce:oce_dev@localhost:5432/oce"
    redis_url: str = "redis://localhost:6379"

    # DeepSeek — sole LLM provider for all 8 agents
    # "deepseek-chat" is DeepSeek's always-latest alias (V3 today, V4 when released)
    # Override with DEEPSEEK_MODEL=deepseek-chat in .env to pin a specific version
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"

    # External tools
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""

    max_companies_per_run: int = 20
    top_opportunities_for_pow: int = 5

    # Comma-separated extra CORS origins, for AlgoReal's deployed URL once
    # it's hosted (e.g. "https://algoreal.vercel.app"). Localhost is always
    # allowed regardless of this setting.
    extra_cors_origins: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
