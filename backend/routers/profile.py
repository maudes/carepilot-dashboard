# user profile: GET/POST/PUT/DELETE
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.user import ProfileCreate, ProfileRead, ProfileUpdate
from backend.db import get_db

# Get User Profile: show email

