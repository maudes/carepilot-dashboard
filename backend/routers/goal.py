# Dashboard, showcase 3P data and default data, goals
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from backend.models.user import Goal, User
from backend.schemas.goal import GoalRead, GoalUpdate
from backend.routers.auth import get_current_user
from backend.db import get_db

router = APIRouter()


@router.get("/me", response_model=GoalRead)
def get_goal(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_goal = db.query(Goal).filter(Goal.user_id == user.id).first()
    if not user_goal:
        user_goal = Goal(user_id=user.id)
        db.add(user_goal)
        db.commit()
        db.refresh(user_goal)

    return GoalRead.model_validate(user_goal)


@router.put("/me", response_model=GoalRead)
def update_goal(
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.goal_text is None:
        raise HTTPException(
            status_code=400,
            detail="goal_text cannot be None."
        )

    user_goal = db.query(Goal).filter(Goal.user_id == user.id).first()
    if not user_goal:
        user_goal = Goal(user_id=user.id)
        db.add(user_goal)
        db.commit()
        db.refresh(user_goal)

    user_goal.goal_text = payload.goal_text
    db.commit()
    db.refresh(user_goal)

    return GoalRead.model_validate(user_goal)
