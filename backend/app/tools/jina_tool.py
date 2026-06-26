import logging

import httpx

from app.config import settings
from app.utils.retry import retry_async

logger = logging.getLogger(__name__)


async def _do_read(url: str) -> str:
    jina_url = f"https://r.jina.ai/{url}"
    headers = {"Accept": "text/plain"}
    if hasattr(settings, "jina_api_key") and settings.jina_api_key:
        headers["Authorization"] = f"Bearer {settings.jina_api_key}"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(jina_url, headers=headers)
        response.raise_for_status()
        return response.text


async def jina_read(url: str) -> str:
    """Read a URL via Jina Reader with automatic retries on transient failures."""
    try:
        return await retry_async(
            _do_read,
            url,
            retries=3,
            base_delay=2.0,
            exceptions=(httpx.HTTPError, Exception),
        )
    except Exception:
        logger.exception("Jina read failed permanently for URL: %s", url)
        return ""
