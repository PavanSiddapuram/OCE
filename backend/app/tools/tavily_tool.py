import asyncio

from tavily import TavilyClient

from app.config import settings

_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient(api_key=settings.tavily_api_key)
    return _client


async def tavily_search(query: str, max_results: int = 10) -> list[dict]:
    """Web search via Tavily. Returns list of {title, url, content, score}."""
    client = _get_client()
    await asyncio.sleep(1)  # rate limit: ~1 req/sec
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.search(query=query, max_results=max_results, search_depth="advanced"),
    )
    return response.get("results", [])
