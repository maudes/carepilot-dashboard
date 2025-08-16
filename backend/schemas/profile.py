from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional


class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"


class ProfileBase(BaseModel):
    email: EmailStr
    name: str | None = None
    birthday: datetime | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    body_fat_percent: float | None = None
    gender: GenderEnum | None = None


class ProfileCreate(ProfileBase):
    name: Optional[str] = "User"
    gender: Optional[GenderEnum] = GenderEnum.OTHER


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
