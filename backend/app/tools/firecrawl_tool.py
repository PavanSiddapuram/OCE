import asyncio
import logging

from firecrawl import FirecrawlApp

from app.config import settings
from app.utils.retry import retry_async

logger = logging.getLogger(__name__)

_app: FirecrawlApp | None = None

# Max 3 concurrent scrapes — Firecrawl free tier allows ~3 req/s
_sem = asyncio.Semaphore(3)


def _get_app() -> FirecrawlApp:
    global _app
    if _app is None:
        _app = FirecrawlApp(api_key=settings.firecrawl_api_key)
    return _app


async def _do_scrape(url: str) -> str:
    app = _get_app()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: app.scrape_url(url, formats=["markdown"]),
    )
    if hasattr(result, "markdown"):
        return result.markdown or ""
    if isinstance(result, dict):
        return result.get("markdown", "")
    return ""


async def firecrawl_scrape(url: str) -> str:
    """Scrape a URL via Firecrawl with concurrency limiting and automatic retries."""
    async with _sem:
        try:
            return await retry_async(
                _do_scrape,
                url,
                retries=3,
                base_delay=3.0,
                exceptions=(Exception,),
            )
        except Exception:
            logger.exception("Firecrawl scrape failed permanently for URL: %s", url)
            return ""
