from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
from uuid import UUID
from datetime import datetime
from backend.schemas.profile import ProfileRead
from backend.schemas.goal import GoalRead
from backend.schemas.vitalsign import VitalSignRead
from backend.schemas.dailylog import DailyLogRead
from typing import Optional, List


# Shared elements of the User schema; not DB auto-generated
class UserBase(BaseModel):
    email: EmailStr
    is_verified: bool = False


# Receive form the front-end
class UserCreate(UserBase):
    pass


# User could change later
class UserUpdate(BaseModel):
    email: EmailStr


# Auto-created by DB; return to the front-end
class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
    # Allow to use object instead of Dict


# For verification only
class VerifyRequest(BaseModel):
    otp: str
    token: str  # handled by front-end in request body

    @field_validator("otp")
    def otp_validator(cls, otp_str):
        if not otp_str.isdigit() or len(otp_str) != 8:
            raise ValueError("The OTP must be 8 digits.")
        return otp_str


class UserLogin(BaseModel):
    email: EmailStr


# All the merge tables
class UserContext(UserRead):
    profile: Optional[ProfileRead] = None
    vital_signs: List[VitalSignRead] = Field(default_factory=list)
    daily_logs: List[DailyLogRead] = Field(default_factory=list)
    goals: List[GoalRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
