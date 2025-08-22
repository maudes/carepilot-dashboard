# Daily input: vitals and logs
# GET/POST, PUT
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from datetime import date
from backend.models.user import DailyRecord, User, VitalSign, DailyLog
from backend.schemas.dailyrecord import (
    DailyRecordRead,
    DailyRecordInit,
    DailyRecordCreate,
    DailyRecordUpdate,
)
from backend.routers.auth import get_current_user
from backend.db import get_db

router = APIRouter()


# Get the record of today; if no record, return an empty form
@router.get("/today", response_model=DailyRecordRead | DailyRecordInit)
def get_daily_records(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.user_id == user.id,
            DailyRecord.record_date == date.today()
        )
        .first()
    )
    if not user_record:
        return DailyRecordInit()
        # Return an empty form

    return DailyRecordRead.model_validate(user_record)


# Create the record
@router.post("/today", response_model=DailyRecordRead)
def create_record(
    payload: DailyRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.user_id == user.id,
            DailyRecord.record_date == date.today(),
        )
        .first()
    )
    if record:
        raise HTTPException(
            status_code=400,
            detail="You’ve already submitted today’s record. Update instead."
        )

    new_record = DailyRecord(
        user_id=user.id,
        record_date=date.today(),
        vital_sign=VitalSign(
            **payload.vital_sign.model_dump(),
            user_id=user.id
        ),
        daily_log=DailyLog(
            **payload.daily_log.model_dump(),
            user_id=user.id
        )
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return DailyRecordRead.model_validate(new_record)


# Update the record
@router.put("/today", response_model=DailyRecordRead)
def update_record(
    payload: DailyRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.user_id == user.id,
            DailyRecord.record_date == date.today(),
        )
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=400,
            detail="No record found for today."
        )

    if payload.vital_sign:
        for key, value in payload.vital_sign.model_dump(exclude_unset=True).items():
            setattr(record.vital_sign, key, value)

    if payload.daily_log:
        for key, value in payload.daily_log.model_dump(exclude_unset=True).items():
            setattr(record.daily_log, key, value)

    db.commit()
    db.refresh(record)
    return DailyRecordRead.model_validate(record)


# Delete the record: delete the record and show the empty form again
@router.delete("/today", response_model=DailyRecordInit)
def delete_record(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.user_id == user.id,
            DailyRecord.record_date == date.today(),
        )
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=400,
            detail="No record found for today."
        )
    db.delete(record)
    db.commit()
    return DailyRecordInit()  # Return an empty form after deletion
