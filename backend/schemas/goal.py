from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class GoalBase(BaseModel):
    goal_text: str | None = None


class GoalCreate(GoalBase):
    goal_text: str = "Be Happy & Be Healthy!"


class GoalUpdate(GoalBase):
    pass


class GoalRead(GoalBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
