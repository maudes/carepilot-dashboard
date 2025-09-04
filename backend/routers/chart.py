# Support panda charts
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.models.user import VitalSign, User
from backend.schemas.chart import VitalSignChart
from backend.routers.auth import get_current_user
from backend.db import get_db
from datetime import date
import pandas as pd

router = APIRouter()


# Provide df for charts in streamlit
@router.get("/me", response_model=list[VitalSignChart])
def get_chart_date(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    start: date = Query(None),
    end: date = Query(None),

):
    user_query = db.query(VitalSign).filter(VitalSign.user_id == user.id)
    # without .all() means only generate an object, no SQL abstract data

    if start:
        user_query = user_query.filter(VitalSign.created_at >= start)
    if end:
        user_query = user_query.filter(VitalSign.created_at <= end)

    records = user_query.order_by(VitalSign.created_at).all()

    # List of Dict
    df = pd.DataFrame([{
        "created_at": record.created_at,
        "user_id": record.user_id,
        "systolic_bp": record.systolic_bp,
        "diastolic_bp": record.diastolic_bp,
        "pre_glucose": record.pre_glucose,
        "post_glucose": record.post_glucose,
        "heart_rate": record.heart_rate,
    } for record in records
    ])

    return df.to_dict(orient="records")
