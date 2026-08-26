from pathlib import Path
from pydantic_settings import BaseSettings

_REPO_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://oce:oce_dev@localhost:5432/oce"
    redis_url: str = "redis://localhost:6379"

    # Multi-Provider LLM Configuration
    # Supported: "gemini" | "kimi" | "deepseek"
    llm_provider: str = "gemini"

    # Gemini (Google AI Studio - Free Tier / Paid)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # Kimi API (Moonshot AI)
    kimi_api_key: str = ""
    kimi_model: str = "moonshot-v1-8k"
    kimi_base_url: str = "https://api.moonshot.cn/v1"

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com"

    # alphaXiv MCP Server
    alphaxiv_mcp_url: str = "https://api.alphaxiv.org/mcp/v1"
    alphaxiv_api_key: str = ""

    # External search tools
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""

    max_companies_per_run: int = 20
    top_opportunities_for_pow: int = 5

    model_config = {"env_file": (_REPO_ROOT_ENV, ".env"), "extra": "ignore"}


settings = Settings()
