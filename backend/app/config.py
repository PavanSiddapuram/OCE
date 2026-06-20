from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://oce:oce_dev@localhost:5432/oce"
    redis_url: str = "redis://localhost:6379"
    anthropic_api_key: str = ""
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    max_companies_per_run: int = 20
    top_opportunities_for_pow: int = 5

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
