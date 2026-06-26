"""Exponential-backoff retry for async callables."""
import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_async(
    fn: Callable[..., Awaitable[T]],
    *args,
    retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    **kwargs,
) -> T:
    """Call *fn* with exponential backoff; raise on final failure."""
    delay = base_delay
    last_exc: Exception = RuntimeError("no attempts made")
    for attempt in range(1, retries + 1):
        try:
            return await fn(*args, **kwargs)
        except exceptions as exc:
            last_exc = exc
            if attempt == retries:
                break
            wait = min(delay, max_delay)
            logger.warning("Attempt %d/%d failed (%s); retrying in %.1fs", attempt, retries, exc, wait)
            await asyncio.sleep(wait)
            delay *= 2
    raise last_exc
