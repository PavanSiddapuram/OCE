from arq import create_pool
from arq.connections import RedisSettings

from app.config import settings

_pool = None


async def get_arq_pool():
    global _pool
    if _pool is None:
        _pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    return _pool


async def enqueue_pipeline(pipeline_run_id: str, filters: dict):
    pool = await get_arq_pool()
    await pool.enqueue_job("run_pipeline", pipeline_run_id, filters)
