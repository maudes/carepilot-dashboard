# Build up Redis connection, client for py application
import redis
from backend.config.settings import settings

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:  # Type hint for Redis client
    global _redis_client  # declare and gonna change the value

    if _redis_client is not None:
        return _redis_client

    if settings.env == "production":
        _redis_client = redis.Redis.from_url(
            settings.upstash_redis_url,
            password=settings.upstash_redis_token,
            decode_responses=True,
        )
    else:
        _redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
            # Optional: decode responses from bytes to strings
            # .decode("utf-8")
        )
    return _redis_client
