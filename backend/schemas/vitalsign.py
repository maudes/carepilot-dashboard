from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class VitalSignBase(BaseModel):
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    pre_glucose: int | None = None
    post_glucose: int | None = None
    heart_rate: int | None = None
    temperature_celsius: float | None = None
    spo2: int | None = None


class VitalSignCreate(VitalSignBase):
    systolic_bp: int
    diastolic_bp: int
    heart_rate: int


class VitalSignUpdate(VitalSignBase):
    pass


class VitalSignRead(VitalSignBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
