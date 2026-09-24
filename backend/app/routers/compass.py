from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PlanStep, User
from app.schemas import CompassGraphResponse
from app.services.compass import build_graph

router = APIRouter(prefix="/compass", tags=["compass"])


@router.get("/graph", response_model=CompassGraphResponse)
def graph(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompassGraphResponse:
    from sqlalchemy import select

    steps = db.scalars(
        select(PlanStep).where(PlanStep.user_id == user.id)
    ).all()
    missing = sorted({s.skill for s in steps if not s.is_done})
    result = build_graph(user.skills, missing, user.desired_position)
    return CompassGraphResponse(**result)