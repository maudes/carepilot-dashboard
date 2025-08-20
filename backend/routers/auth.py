# Auth related APIs
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.user import UserCreate, VerifyRequest, UserLogin
from backend.schemas.token import TokenResponse
from fastapi.security import OAuth2PasswordBearer
from backend.db import get_db
from backend.redis_client import get_redis_client
from upstash_redis.asyncio import Redis
from backend.services.otp import otp_generator
from backend.services.smtp import send_otp_email
from backend.services.redis_otp import store_otp, verify_otp, fetch_otp
from backend.services.jwt_token import (
    create_otp_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    token_type,
    refresh_access_token,
    validate_token,
    revoke_this_token,
    revoke_all_tokens,
)
from typing import Literal
from uuid import UUID


# Define a group of auth APIs
router = APIRouter()


# Register with OTP
# response_model is for the output data format; JSONResponse -> None
@router.post("/register-request", response_model=None)
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_client),
):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        if existing_user.deleted_at is not None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This email was previously registered and deleted. "
                    "Please contact support."
                )
            )

        raise HTTPException(
            status_code=400,
            detail="This email is already registered."
        )

    # Generate an OTP pwd - services/otp.py
    otp = otp_generator()

    # Send OTP pwd to the new user's email - services/smtp.py
    is_success, msg = await send_otp_email(
        "Your CarePilot One-Time-Password",
        [payload.email],
        "otp.html",
        {"otp": otp},
    )

    if not is_success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed due to {msg}. Please try again."
        )

    # Save the OTP pwd to the redis server with 30mins - services/redis.py
    await store_otp(redis, payload.email, otp)

    # Create a token to wrap email for verification
    otp_payload = {
        "sub": str(payload.email),
    }
    otp_token = await create_otp_token(redis, otp_payload)

    # Return message and redirect to verify process
    response = JSONResponse(
        status_code=200,
        content={
            "message": "OTP sent. Please verify.",
            "mode": "register",
            "redirect_to": "/verify",
            "token": otp_token,
        }
    )
    return response


# Login
@router.post("/login-request", response_model=None)
async def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_client),
):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        if existing_user.deleted_at is not None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This email was previously registered and deleted. "
                    "Please contact support."
                )
            )

        otp = otp_generator()

        is_success, msg = await send_otp_email(
            "Your CarePilot One-Time-Password",
            [payload.email],
            "otp.html",
            {"otp": otp},
        )

        if not is_success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed due to {msg}. Please try again."
            )
        await store_otp(redis, payload.email, otp)

        otp_payload = {
            "sub": str(payload.email),
        }
        otp_token = await create_otp_token(redis, otp_payload)

        response = JSONResponse(
            status_code=200,
            content={
                "message": "OTP sent. Please verify.",
                "mode": "login",
                "redirect_to": "/verify",
                "token": otp_token,
            }
        )
        return response

    else:
        raise HTTPException(status_code=404, detail="The user does not exist.")


# Verify OTP
@router.post("/verify", response_model=TokenResponse)
async def verify_user(
    payload: VerifyRequest,
    mode: Literal["register", "login"],
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_client),
):
    otp_payload = decode_token(payload.token)
    if otp_payload is None:
        raise HTTPException(
            status_code=400,
            detail="The token cannot be verified."
        )

    otp_email = otp_payload.get("sub")
    await validate_token(redis, otp_payload, "otp", False)
    await revoke_this_token(redis, payload.token)

    # Fetch stored otp and verify it
    stored_otp = await fetch_otp(redis, otp_email)

    if await verify_otp(redis, payload.otp, stored_otp, otp_email):
        user = db.query(User).filter(User.email == otp_email).first()
        if mode == "register":
            if user:
                raise HTTPException(
                    status_code=400,
                    detail="User already exists."
                )
            user = User(email=otp_email, is_verified=True)
            db.add(user)
            db.commit()
            db.refresh(user)

        if mode == "login" and not user.is_verified:
            user.is_verified = True
            db.commit()
            db.refresh(user)

        # Basic checks
        if not user:
            raise HTTPException(
                status_code=400,
                detail="Cannot find the user."
            )

        if user.deleted_at is not None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This email was previously registered and deleted. "
                    "Please contact support."
                )
            )

        # Create Token
        access_payload = {
            "sub": str(user.id),
        }
        refresh_payload = {
            "sub": str(user.id),
        }
        access_token = await create_access_token(redis, access_payload)
        refresh_token = await create_refresh_token(redis, refresh_payload)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            redirect_to="/home",
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP value. Please retry."
        )


# Decode the access_token from Header in request body
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# get_current_user() -> Focus on verifying access token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_client),
) -> User:

    user_payload = decode_token(token)
    if user_payload == "expired":
        raise HTTPException(status_code=401, detail="Token expired. Please login again.")
    if user_payload is None or not token_type(user_payload, "access"):
        raise HTTPException(status_code=401, detail="Please login first.")

    user_id = user_payload.get("sub")
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=400,
            detail=(
                "This email was previously registered and deleted. "
                "Please contact support."
            )
        )

    await validate_token(redis, user_payload, "access", False)

    return user


# Front-end asks for refresh access token
@router.post("/token-refresh", response_model=None)
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis_client),
):
    new_access_token = await refresh_access_token(redis, token)
    return {"access_token": new_access_token}


# Logout
@router.post("/logout", response_model=None)
async def logout(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis_client),
):
    result = await revoke_all_tokens(redis, token)
    return result
