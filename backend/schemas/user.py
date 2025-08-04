from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime


# Share elements of the User schema; not DB auto-generated
class UserBase(BaseModel):
    email: EmailStr
    is_verified: bool = False


class UserCreate(UserBase):
    pass


# User could change later
class UserUpdate(BaseModel):
    email: EmailStr


# Auto-created by DB
class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
