# Auth related APIs
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.user import UserCreate, UserRead, UserVerify
from backend.schemas.token import TokenResponse
from backend.db import get_db
from backend.services.otp import otp_generator
from backend.services.smtp import send_otp_email
from backend.services.redis import store_otp, verify_otp, fetch_otp
from backend.services.jwt_token import (
    create_access_token,
    create_refresh_token,
    token_type,
)
from fastapi.responses import JSONResponse

# Define a group of auth APIs
router = APIRouter()


# Register with OTP
# response_model is for the output data format; JSONResponse -> None
@router.post("/register-request", response_model=None)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="The email has registered.")

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
        raise HTTPException(status_code=500, detail= f"Failed due to {msg}. Please try again.")

    # Save the OTP pwd to the redis server with 30mins - services/redis.py
    store_otp(payload.email, otp)

    # Create new user and add it into the DB
    new_user = User(email=payload.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return message and redirect to verify process
    return JSONResponse(
        status_code=200,
        content={
            "message": "OTP sent. Please verify.",
            "email": payload.email,
            "redirect_to": "/api/auth/verify"
        }
    )


# Verify OTP # Use UserRead for protecting sensitvie data
@router.post("/verify", response_model=TokenResponse)
def verify_user(payload: UserVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Cannot find the user.")

    # Fetch stored otp and verify it
    stored_otp = fetch_otp(payload.email)
    if verify_otp(payload.otp, stored_otp, payload.email):
        user.is_verified = True
        db.commit()
        db.refresh(user)

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
    else:
        raise ValueError("Invalid OTP value. Please retry.")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type=token_type,
        redirect_to="pages/home.py",
    )


# Login
    # Recevie email input
    # Verify it's a valid email and send OTP pwd - service/otp.py/smtp.py
    # Renew the redis OTP pwd - services/redis.py
    # Receive the OTP pwd
    # Verify the OTP with redis one
    # return JWT token


# get_current_user()
"""
@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
"""
