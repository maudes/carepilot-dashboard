# Auth related APIs
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.user import UserCreate, UserRead
from backend.db import get_db
from backend.services.otp import otp_generator
from backend.services.smtp import send_otp_email

# Define a group of auth APIs
router = APIRouter()


# Register with OTP
@router.post("/register", response_model=User)
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

    # Return message and redirect to verify process 


# Verify OTP
@router.post("/register-verify", response_model=User)


    # Receive the input OTP pwd

    # Get the correct OTP pwd from the redis server - services/redis.py

    # Verify if the two are the same

    # Commit the email registeration to db, change is_verified == True

    # return JWT token - services/jwt.py



# Login
@router.post("/login", response_model=User)

    # Recevie email input
    # Verify it's a valid email and send OTP pwd - service/otp.py/smtp.py
    # Renew the redis OTP pwd - services/redis.py
    # Receive the OTP pwd
    # Verify the OTP with redis one
    # return JWT token


# Logout
