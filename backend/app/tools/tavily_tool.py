import asyncio
import logging

from tavily import TavilyClient

from app.config import settings
from app.utils.retry import retry_async

logger = logging.getLogger(__name__)

_client: TavilyClient | None = None

# Max 2 concurrent requests to stay within free-tier rate limits
_sem = asyncio.Semaphore(2)


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient(api_key=settings.tavily_api_key)
    return _client


async def _do_search(query: str, max_results: int) -> list[dict]:
    client = _get_client()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.search(query=query, max_results=max_results, search_depth="advanced"),
    )
    return response.get("results", [])


async def tavily_search(query: str, max_results: int = 10) -> list[dict]:
    """Web search via Tavily with concurrency limiting and automatic retries."""
    async with _sem:
        await asyncio.sleep(1)  # sustained ~1 req/sec per slot
        try:
            return await retry_async(
                _do_search,
                query,
                max_results,
                retries=3,
                base_delay=5.0,
                exceptions=(Exception,),
            )
        except Exception:
            logger.exception("Tavily search failed permanently for query: %s", query)
            return []
