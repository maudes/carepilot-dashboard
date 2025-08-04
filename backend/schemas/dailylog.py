from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class DailyLogBase(BaseModel):
    steps: int | None = None
    medication: bool | None = None
    meals_text: str | None = None
    appetite_level: int | None = None
    bowel_status: str | None = None
    mood_rate: int | None = None
    notes: str | None = None


class DailyLogCreate(DailyLogBase):
    medication: bool = False


class DailyLogUpdate(DailyLogBase):
    pass


class DailyLogRead(DailyLogBase):
    id: UUID
    user_id: UUID
    medication: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
