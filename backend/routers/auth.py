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
from backend.schemas.token import TokenResponse, TokenPayload
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
)
from typing import Literal


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
        raise HTTPException(
            status_code=400,
            detail="The email has registered."
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

    # Create new user and add it into the DB
    new_user = User(email=payload.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create a token to wrap email for verification
    otp_payload = {
        "sub": str(payload.email),
        "type": "login_otp"
    }
    otp_token = create_otp_token(otp_payload)

    # Return message and redirect to verify process
    response = JSONResponse(
        status_code=200,
        content={
            "message": "OTP sent. Please verify.",
            "mode": "register",
            "redirect_to": "/api/auth/verify",
            "token": otp_token,
        }
    )
    return response


# Login
@router.post("/login-request", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_client),
):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
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
            "type": "login_otp"
        }
        otp_token = create_otp_token(otp_payload)

        response = JSONResponse(
            status_code=200,
            content={
                "message": "OTP sent. Please verify.",
                "mode": "login",
                "redirect_to": "/api/auth/verify",
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

    email = otp_payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Cannot find the user."
        )

    # Fetch stored otp and verify it
    stored_otp = await fetch_otp(redis, email)

    if verify_otp(redis, payload.otp, stored_otp, email):
        if mode == "register":
            user.is_verified = True
            db.commit()
            db.refresh(user)

        # Create Token
        access_payload = {
            "sub": str(user.id),
            "type": "access"
        }
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh"
        }
        access_token = create_access_token(access_payload)
        refresh_token = create_refresh_token(refresh_payload)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            redirect_to="pages/home",
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP value. Please retry."
        )


# Decode the access_token from Header in request body
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# get_current_user() -> Focus on verifying access token
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    user_payload = decode_token(token)
    if user_payload is None or not token_type(user_payload, "access"):
        raise HTTPException(status_code=401, detail="Please login first.")

    return TokenPayload(**user_payload)
