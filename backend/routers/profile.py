# user profile: GET/POST/PUT/DELETE
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.models.user import User, Profile
from backend.schemas.profile import ProfileRead, ProfileUpdate
from backend.schemas.token import TokenPayload
from backend.routers.auth import get_current_user
from backend.db import get_db

router = APIRouter()


# Get/ Post user profile
@router.get("/profile/me", response_model=ProfileRead)
def get_profile(
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Please login first.")

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        # raise HTTPException(status_code=404, detail="Profile not found.")

    return profile


# Update user profile
@router.put("/profile/me", response_model=ProfileRead)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=400, detail="Please login first.")

    current_user = db.query(User).filter(User.id == user.id).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # In case use the API directly
    user_profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not user_profile:
        user_profile = Profile(user_id=user.id)
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)

    # Check the required fields:
    if not payload.name or not payload.email:
        raise HTTPException(
            status_code=401,
            detail="Email and name are required."
        )

    # If there's a new email input:
    new_email = payload.email.strip()
    if new_email != current_user.email:
        exisitng_user = db.query(User).filter(
            User.email == new_email
            ).first()
        if exisitng_user:
            raise HTTPException(
                status_code=400,
                detail="The email has registered."
            )
        current_user.is_verified = False
        current_user.email = new_email

        # Would need to add the "logout" here to activated the new email
        # Need to check the is_verified -> adjust auth.py

    # Save all the updated fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(user_profile, key):
            setattr(user_profile, key, value)

    db.commit()
    db.refresh(user_profile)
    db.refresh(current_user)
    return user_profile


# Delete account
@router.delete("/profile/me", response_model=None)
def delete_profile(
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=400, detail="Please login first.")

    current_user = db.query(User).filter(User.id == user.id).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found.")

    current_user.deleted_at = datetime.now(timezone.utc)
    db.commit()
