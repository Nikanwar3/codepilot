"""
Async Redis client, shared across the app (rate limiting, SSE pub/sub for
agent progress events, Celery result polling helpers added in later steps).
"""

from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

_pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis() -> Redis:
    return Redis(connection_pool=_pool)
