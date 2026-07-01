from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://oce:oce_dev@localhost:5432/oce"
    redis_url: str = "redis://localhost:6379"

    # DeepSeek — sole LLM provider for all agents
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"          # DeepSeek-V3
    deepseek_base_url: str = "https://api.deepseek.com"

    # External tools
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""

    max_companies_per_run: int = 20
    top_opportunities_for_pow: int = 5

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
