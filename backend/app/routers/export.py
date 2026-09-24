from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PlanStep, User
from app.services.export import plan_to_pdf

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/plan.pdf")
def export_plan_pdf(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    steps = list(
        db.scalars(
            select(PlanStep)
            .where(PlanStep.user_id == user.id)
            .order_by(PlanStep.order_index)
        )
    )
    pdf = plan_to_pdf(user, steps)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="plan-{user.id}.pdf"'
        },
    )