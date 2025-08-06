import redis
import backend.config.settings as settings


def get_redis_client() -> redis.Redis:  # Type hint for Redis client
    if settings.env == "production":
        return redis.Redis.form_url(
            settings.upstash_redis_url,
            password=settings.upstash_redis_token,
            decode_responses=True,
        )
    else:
        return redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            paassword=settings.redis_password,
            decode_responses=True,
            # Optional: decode responses from bytes to strings
            # .decode("utf-8")
        )
