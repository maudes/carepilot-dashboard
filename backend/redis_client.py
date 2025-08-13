# Build up Redis connection, client for py application
from upstash_redis import Redis
from backend.config.settings import settings


def get_redis_client() -> Redis:
    return Redis(
        url=settings.upstash_redis_rest_url,
        token=settings.upstash_redis_rest_token,
    )
