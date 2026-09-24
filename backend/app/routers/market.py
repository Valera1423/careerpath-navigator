from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import MarketTrendsResponse
from app.services.market import market_trends

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/trends", response_model=MarketTrendsResponse)
def trends(
    days: int = Query(default=30, ge=7, le=180),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return market_trends(
        db=db,
        position=user.desired_position,
        region=user.region,
        days=days,
    )