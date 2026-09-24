from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import LeaderboardEntry
from app.services.leaderboard import top_users

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[LeaderboardEntry])
def leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[LeaderboardEntry]:
    return [LeaderboardEntry(**row) for row in top_users(db, limit)]