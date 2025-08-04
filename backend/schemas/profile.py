from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"


class ProfileBase(BaseModel):
    name: str | None = None
    birthday: datetime | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    body_fat_percent: float | None = None
    gender: GenderEnum | None = None


class ProfileCreate(ProfileBase):
    name: str
    gender: GenderEnum


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
