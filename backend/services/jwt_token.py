from datetime import datetime, timezone, timedelta
from backend.config.settings import settings
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from fastapi import HTTPException
import uuid

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expire_minutes
# OTP_TOKEN_EXPIRE_MINUTES


# Create user access token; data is for attaching user-info
def create_token(
    data: dict,
    token_type: str,
    expires_delta: timedelta,
):
    user_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    jti = str(uuid.uuid4())
    user_encode.update({
        "exp": expire,
        "type": token_type,
        "jti": jti,
    })
    encoded_jwt = jwt.encode(user_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt, jti
    # jwt returns string:
    # like: <base64-encoded header>.<base64-encoded payload>.<signature>


async def create_access_token(redis, data: dict) -> str:
    access_token, jti = create_token(
        data,
        "access",
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    user_id = data["sub"]
    key = f"jti:access:{user_id}:{jti}"
    expired_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    await redis.setex(key, expired_seconds, "valid")
    return access_token


async def create_refresh_token(redis, data: dict) -> str:
    refresh_token, jti = create_token(
        data,
        "refresh",
        timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    user_id = data["sub"]
    key = f"jti:refresh:{user_id}:{jti}"
    expired_seconds = REFRESH_TOKEN_EXPIRE_MINUTES * 60
    await redis.setex(key, expired_seconds, "valid")
    return refresh_token


async def create_otp_token(redis, data: dict) -> str:
    otp_token, jti = create_token(
        data,
        "otp",
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    user_email = data["sub"]
    key = f"jti:otp:{user_email}:{jti}"
    expired_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    await redis.setex(key, expired_seconds, "valid")
    return otp_token


# For front-end use, if access token is expired
# # Note: if user.id is worng or deleted?
async def refresh_access_token(redis, refresh_token: str):
    payload = decode_token(refresh_token)
    if payload == "expired":
        raise HTTPException(status_code=401, detail="Token expired.")
    if payload is None or not token_type(payload, "refresh"):
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    await validate_token(redis, payload, "refresh", False)

    new_access_token = await create_access_token(redis, {
        "sub": payload["sub"],
    })

    return new_access_token


# Decode and verify the JWT token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return payload
    except ExpiredSignatureError:
        return "expired"
    except JWTError:
        return None


# Verify if token_type is corrent
def token_type(payload: dict, expected_type: str) -> bool:
    return payload.get("type") == expected_type


# Validate token jti
async def validate_token(
    redis,
    payload: dict,
    token_type: str,
    return_result: bool
):
    jti = payload.get("jti")
    sub = payload.get("sub")

    if not jti or not sub:
        raise HTTPException(
            status_code=400,
            detail="Missing required token fields."
        )

    key = f"jti:{token_type}:{sub}:{jti}"
    redis_jti = await redis.get(key)

    if redis_jti is None:
        raise HTTPException(
            status_code=401,
            detail="Token not found."
        )

    if redis_jti != "valid":
        raise HTTPException(
            status_code=401,
            detail=f"{token_type} token revoked."
        )
    if return_result is True:
        return {"success": True}


# Revoke current token (single jti, single token)
async def revoke_this_token(redis, token: str):
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        jti = payload.get("jti")
        pattern = f"jti:*:{sub}:{jti}"
        cursor = 0
        revoked_count = 0
        while True:
            cursor, keys = await redis.scan(cursor, match=pattern)
            for key in keys:
                await redis.set(key, "revoked")
                revoked_count += 1
            if cursor == 0:
                break
        return {
            "success": True,
            "message": f"Revoked {revoked_count} token(s)."
        }

    except Exception as e:
        return {"success": False, "message": f"{e}"}


# Revoke all tokens under same sub(normally user.id -> access/refresh tokens)
async def revoke_all_tokens(redis, token: str):
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        pattern = f"jti:*:{sub}:*"
        cursor = 0
        revoked_count = 0
        while True:
            cursor, keys = await redis.scan(cursor, match=pattern)
            for key in keys:
                await redis.set(key, "revoked")
                revoked_count += 1
            if cursor == 0:
                break
        return {
            "success": True,
            "message": f"Revoked {revoked_count} token(s)."
        }

    except Exception as e:
        return {"success": False, "message": f"{e}"}
