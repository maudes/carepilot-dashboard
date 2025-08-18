# Build up Redis connection, client for py application
from upstash_redis.asyncio import Redis
from backend.config.settings import settings

# _redis_client: Redis | None = None


def get_redis_client() -> Redis:
    redis_client = Redis(
        url=settings.upstash_redis_rest_url,
        token=settings.upstash_redis_rest_token,
    )

    return redis_client
