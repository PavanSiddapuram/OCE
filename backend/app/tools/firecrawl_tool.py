import asyncio

from firecrawl import FirecrawlApp

from app.config import settings

_app: FirecrawlApp | None = None


def _get_app() -> FirecrawlApp:
    global _app
    if _app is None:
        _app = FirecrawlApp(api_key=settings.firecrawl_api_key)
    return _app


async def firecrawl_scrape(url: str) -> str:
    """Scrape a single URL and return its markdown content."""
    app = _get_app()
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None,
            lambda: app.scrape_url(url, formats=["markdown"]),
        )
        if hasattr(result, "markdown"):
            return result.markdown or ""
        if isinstance(result, dict):
            return result.get("markdown", "")
        return ""
    except Exception:
        return ""
