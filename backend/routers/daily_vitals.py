# Daily input: vitals and logs
# GET/POST, PUT
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session, selectinload
from datetime import datetime, timezone
from backend.models.user import DailyRecord
from backend.schemas.dailyrecord import DailyRecordRead
from backend.routers.auth import get_current_user, oauth2_scheme
from backend.db import get_db

router = APIRouter


# Get the data
@router.get("/daily_record/me", response_model= DailyRecordRead | None)
def get_daily_records():
    pass
