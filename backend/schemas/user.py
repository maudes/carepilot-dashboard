from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime


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
class UserVerify(UserBase):
    otp: str

    @field_validator("otp")
    def otp_validator(cls, otp_str):
        if not otp_str.isdigit() or len(otp_str) != 6:
            raise ValueError("The OTP must be 6 digits.")
        return otp_str
