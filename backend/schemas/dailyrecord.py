# Based on DailyRecord model, combining DailyLog and VitalSigns tables
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class DailyRecordBase(BaseModel):
    # VitalSign
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    pre_glucose: int | None = None
    post_glucose: int | None = None
    heart_rate: int | None = None
    temperature_celsius: float | None = None
    spo2: int | None = None
    # DailyLog
    steps: int | None = None
    medication: bool | None = None
    meals_text: str | None = None
    appetite_level: int | None = None
    bowel_status: str | None = None
    mood_rate: int | None = None
    notes: str | None = None


class DailyRecordCreate(DailyRecordBase):
    medication: bool = False


class DailyRecordUpdate(DailyRecordBase):
    systolic_bp: int
    diastolic_bp: int
    heart_rate: int


class DailyRecordRead(DailyRecordBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
