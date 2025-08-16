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
@router.get("/user-profile", response_model=ProfileRead)
def get_profile(
    payload: ProfileCreate,
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile:
        pass


# Post


# Get


# Delete account
