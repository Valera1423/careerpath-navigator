from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    PortfolioBulletRequest,
    PortfolioBulletResponse,
    PortfolioReadmeRequest,
    PortfolioReadmeResponse,
)
from app.services.portfolio import generate_readme, generate_resume_bullet

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/readme", response_model=PortfolioReadmeResponse)
def readme(
    payload: PortfolioReadmeRequest,
    user: User = Depends(get_current_user),
) -> PortfolioReadmeResponse:
    text = generate_readme(
        project_name=payload.project_name,
        description=payload.description,
        skills=payload.skills,
        author=user.full_name or "Автор",
    )
    return PortfolioReadmeResponse(readme=text)


@router.post("/resume-bullet", response_model=PortfolioBulletResponse)
def resume_bullet(
    payload: PortfolioBulletRequest,
    user: User = Depends(get_current_user),
) -> PortfolioBulletResponse:
    bullet = generate_resume_bullet(
        project_name=payload.project_name,
        skills=payload.skills,
        outcome=payload.outcome,
    )
    return PortfolioBulletResponse(bullet=bullet)