from datetime import datetime, timezone, timedelta
from backend.config.settings import settings
from jose import jwt, JWTError
from fastapi import HTTPException

SECRET_KEY = settings.secret_key
ALGORITHM = [settings.algorithm]
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
    user_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(user_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict) -> str:
    access_token = create_token(
        data,
        "access",
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return access_token


def create_refresh_token(data: dict) -> str:
    refresh_token = create_token(
        data,
        "refresh",
        timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return refresh_token


def create_otp_token(data: dict) -> str:
    otp_token = create_token(
        data,
        "login_otp",
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return otp_token


# For front-end use, if access token is expired
def refresh_access_token(refresh_token: str):
    payload = decode_token(refresh_token)
    if payload is None or not token_type(payload, "refresh"):
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    # Convert UNIX timestamp to datetime format
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc) 
    if exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired.")

    new_access_token = create_access_token({
        "sub": payload["sub"],
        "type": "access"
    })

    return new_access_token


# Decode and verify the JWT token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError:
        return None


# Verify if token_type is corrent
def token_type(payload: dict, expected_type: str) -> bool:
    return payload.get("type") == expected_type
