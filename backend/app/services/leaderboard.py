"""Лидерборд: рейтинг пользователей по XP."""
from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import User, UserProgress


def top_users(db: Session, limit: int = 20) -> list[dict]:
    rows = db.execute(
        select(User, UserProgress)
        .join(UserProgress, UserProgress.user_id == User.id)
        .order_by(desc(UserProgress.xp))
        .limit(limit)
    ).all()

    result: list[dict] = []
    for idx, (user, progress) in enumerate(rows, 1):
        # Анонимизация: показываем только имя и первую букву фамилии
        display = _display_name(user.full_name)
        result.append(
            {
                "rank": idx,
                "display_name": display,
                "xp": progress.xp,
                "level": progress.level,
                "streak_days": progress.streak_days,
            }
        )
    return result


def _display_name(full_name: str | None) -> str:
    if not full_name:
        return "Аноним"
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[1][0]}."