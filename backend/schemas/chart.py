from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class VitalSignChart(BaseModel):
    created_at: datetime
    user_id: UUID
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    pre_glucose: int | None = None
    post_glucose: int | None = None
    heart_rate: int | None = None

    model_config = ConfigDict(from_attributes=True)
