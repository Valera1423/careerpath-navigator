from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import ForecastResponse
from app.services.market_forecast import forecast_skills

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/forecast", response_model=ForecastResponse)
def forecast(
    horizon_months: int = Query(default=6, ge=1, le=24),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ForecastResponse:
    items = forecast_skills(db, user.desired_position, horizon_months)
    return ForecastResponse(horizon_months=horizon_months, items=items)