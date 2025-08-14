# from backend.redis_client import get_redis_client
# from datetime import timedelta
import logging

# redis = get_redis_client()

""" Add checking mechanism as below
MAX_ATTEMPTS = 5 -> locked
BLOCK_DURATION = timedelta(minutes=30) -> 403
reset -> once successed, clear the counting
"""


async def store_otp(redis, email: str, otp: str, ttl: int = 1800) -> None:
    key = f"otp:{email}"
    await redis.set(key, otp, ex=ttl)
    return key


async def delete_otp(redis, email: str):
    key = f"otp:{email}"
    await redis.delete(key)


# Remember to add the edge case
async def fetch_otp(redis, email: str) -> str | None:
    key = f"otp:{email}"
    stored_otp = await redis.get(key)
    return stored_otp


async def verify_otp(
    redis,
    otp: str,
    stored_otp: str | None,
    email: str,
) -> bool:
    if stored_otp is None:
        logging.warning(f"No OTP found for {email}.")
        return False
    elif stored_otp == otp:
        await delete_otp(redis, email)
        logging.info(f"OTP verified for {email}")
        return True
    else:
        logging.warning(f"OTP verification failed for {email}")
        return False
