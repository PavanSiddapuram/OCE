import httpx

from app.config import settings


async def jina_read(url: str) -> str:
    """Read a URL via Jina Reader API — good for LinkedIn and structured docs."""
    jina_url = f"https://r.jina.ai/{url}"
    headers = {"Accept": "text/plain"}
    if hasattr(settings, "jina_api_key") and settings.jina_api_key:
        headers["Authorization"] = f"Bearer {settings.jina_api_key}"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(jina_url, headers=headers)
            response.raise_for_status()
            return response.text
    except Exception:
        return ""
