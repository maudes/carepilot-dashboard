# user profile: GET/POST/PUT/DELETE
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from backend.models.user import User, Profile
from backend.schemas.user import ProfileCreate, ProfileRead, ProfileUpdate
from backend.schemas.token import TokenPayload
from backend.routers.auth import get_current_user
from backend.db import get_db

router = APIRouter()


# Get User Profile: show email, name, gender with values others with none
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


# Put


# Delete account
