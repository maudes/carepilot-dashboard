# user profile: GET/POST/PUT/DELETE
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session, selectinload
from datetime import datetime, timezone
from backend.models.user import User, Profile
from backend.schemas.profile import UserProfileUpdate
from backend.schemas.user import UserContext
from backend.routers.auth import get_current_user, logout, oauth2_scheme
from backend.redis_client import get_redis_client
from backend.services.jwt_token import revoke_all_tokens
from upstash_redis.asyncio import Redis
from backend.db import get_db

router = APIRouter()


# Get/ Post user profile
@router.get("/me", response_model=UserContext)
def get_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Please login first.")

    if not user.profile:
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        user.profile = profile
        # raise HTTPException(status_code=404, detail="Profile not found.")
    user = (
        db.query(User)
        .options(
            selectinload(User.profile)
        )
        .filter(User.id == user.id)
        .first()
    )

    print(f"user.profile: {user.profile}")
    return UserContext.model_validate(user)


# Update user profile
@router.put("/me", response_model=UserContext)
async def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis_client),
    token: str = Depends(oauth2_scheme),
):
    if not user:
        raise HTTPException(status_code=401, detail="Please login first.")

    # In case use the API directly
    user_profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not user_profile:
        user_profile = Profile(user_id=user.id)
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)

    user_data = payload.model_dump(exclude_unset=True)
    email = user_data.pop("email", None)

    if email is not None:
        if email.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="Email cannot be empty."
            )
        if email != user.email:
            existing_user = db.query(User).filter(
                User.email == email
                ).first()
            if existing_user:
                raise HTTPException(
                    status_code=409,
                    detail="The email has registered."
                )
            user.is_verified = False
            user.email = email
            db.commit()
            await logout(redis, token)

    # Save all the updated fields
    for key, value in user_data.items():
        if hasattr(user_profile, key):
            setattr(user_profile, key, value)

    db.commit()
    user = (
        db.query(User)
        .options(
            selectinload(User.profile)
        )
        .filter(User.id == user.id)
        .first()
    )

    return UserContext.model_validate(user)


# Delete account
@router.delete("/me", response_model=None)
async def delete_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis_client),
    token: str = Depends(oauth2_scheme),
):
    user.deleted_at = datetime.now(timezone.utc)

    # Delete user related data
    if user.profile:
        db.delete(user.profile)

    if user.daily_record:
        for record in user.daily_record:
            db.delete(record)

    # if user.goal:

    db.commit()
    db.refresh(user)
    response = await revoke_all_tokens(redis, token)
    return response
