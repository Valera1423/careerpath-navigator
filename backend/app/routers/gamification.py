from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Achievement, User, UserProgress
from app.schemas import AchievementOut, ProgressOut
from app.services.gamification import ACHIEVEMENTS, xp_to_level

router = APIRouter(prefix="/gamification", tags=["gamification"])


def _get_or_create_progress(db: Session, user: User) -> UserProgress:
    progress = db.scalar(
        select(UserProgress).where(UserProgress.user_id == user.id)
    )
    if not progress:
        progress = UserProgress(user_id=user.id)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


@router.get("/progress", response_model=ProgressOut)
def get_progress(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProgressOut:
    progress = _get_or_create_progress(db, user)
    code, label, current, next_threshold = xp_to_level(progress.xp)
    return ProgressOut(
        xp=progress.xp,
        level=code,
        level_label=label,
        current_threshold=current,
        next_threshold=next_threshold,
        streak_days=progress.streak_days,
    )


@router.get("/achievements", response_model=list[AchievementOut])
def list_achievements(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AchievementOut]:
    rows = db.scalars(
        select(Achievement).where(Achievement.user_id == user.id)
    ).all()
    result: list[AchievementOut] = []
    for a in rows:
        title, desc = ACHIEVEMENTS.get(a.code, (a.code, ""))
        result.append(
            AchievementOut(
                id=a.id,
                code=a.code,
                title=title,
                description=desc,
                unlocked_at=a.unlocked_at,
            )
        )
    return result