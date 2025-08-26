# History records: vitals and logs
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
@router.get("/", response_model=DailyRecordRead | DailyRecordInit)
def get_past_records(
    record_date: date,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.user_id == user.id,
            DailyRecord.record_date == record_date
        )
        .first()
    )
    if not user_record:
        return DailyRecordInit()
        # Return an empty form

    return DailyRecordRead.model_validate(user_record)


# Create the record
@router.post("/", response_model=DailyRecordRead)
def create_record(
    payload: DailyRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.user_id == user.id,
            DailyRecord.record_date == payload.record_date,
        )
        .first()
    )
    if record:
        raise HTTPException(
            status_code=400,
            detail="There's a record. Update instead."
        )

    new_record = DailyRecord(
        user_id=user.id,
        record_date=payload.record_date,
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
@router.put("/", response_model=DailyRecordRead)
def update_record(
    payload: DailyRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.user_id == user.id,
            DailyRecord.record_date == payload.record_date,
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
@router.delete("/", response_model=DailyRecordInit)
def delete_record(
    record_date: date,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(DailyRecord)
        .filter(
            DailyRecord.user_id == user.id,
            DailyRecord.record_date == record_date,
        )
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=400,
            detail="No record found for this day."
        )
    db.delete(record)
    db.commit()
    return DailyRecordInit()  # Return an empty form after deletion
