from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PlanStep, User
from app.schemas import CoachAskRequest, CoachAskResponse
from app.services.coach import answer_async, build_context
from app.services.llm_client import llm_client

router = APIRouter(prefix="/coach", tags=["coach"])


@router.post("/ask", response_model=CoachAskResponse)
async def ask(
    payload: CoachAskRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CoachAskResponse:
    steps = list(db.scalars(select(PlanStep).where(PlanStep.user_id == user.id)))
    ctx = await build_context(user, steps)
    text = await answer_async(payload.question, ctx)
    return CoachAskResponse(answer=text, used_llm=llm_client.enabled)