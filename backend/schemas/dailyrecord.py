# Based on DailyRecord model, combining DailyLog and VitalSigns tables
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date


class VitalSignBase(BaseModel):
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    pre_glucose: int | None = None
    post_glucose: int | None = None
    heart_rate: int | None = None
    temperature_celsius: float | None = None
    spo2: int | None = None


class VitalSignRead(VitalSignBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DailyLogBase(BaseModel):
    steps: int | None = None
    medication: bool = Field(default=False, description="Take medicine?")
    meals_text: str | None = None
    appetite_level: int | None = None
    bowel_status: str | None = None
    mood_rate: int | None = None
    notes: str | None = None


class DailyLogRead(DailyLogBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DailyRecordBase(BaseModel):
    record_date: date
    vital_sign: VitalSignBase
    daily_log: DailyLogBase


class DailyRecordCreate(DailyRecordBase):
    record_date: date = Field(default=date.today())


class DailyRecordUpdate(BaseModel):
    vital_sign: VitalSignBase | None = None
    daily_log: DailyLogBase | None = None


class DailyRecordRead(BaseModel):
    vital_sign: VitalSignRead
    daily_log: DailyLogRead
    record_date: date
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DailyRecordInit(BaseModel):
    vital_sign: VitalSignBase = Field(default_factory=VitalSignBase)
    daily_log: DailyLogBase = Field(default_factory=DailyLogBase)

    model_config = ConfigDict(from_attributes=True)
