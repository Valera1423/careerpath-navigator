"""Геймификация: XP, уровни, достижения, streak."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models import Achievement, UserProgress

XP_PER_STEP = 50
XP_PER_STREAK_DAY = 10

LEVELS = [
    ("intern", 0, "Стажёр"),
    ("junior", 200, "Junior"),
    ("middle", 600, "Middle"),
    ("senior", 1200, "Senior"),
    ("lead", 2000, "Team Lead"),
]

ACHIEVEMENTS = {
    "sql_ninja": ("SQL-ниндзя", "Отмечен шаг по навыку SQL"),
    "pythonista": ("Pythonista", "Отмечен шаг по Python"),
    "portfolio_ready": ("Портфолио готово", "3+ проекта в портфолио"),
    "streak_7": ("Неделя силы", "7 дней подряд активности"),
    "interview_ready": ("Готов к собеседованию", "Пройден симулятор"),
    "first_step": ("Первый шаг", "Отмечен первый шаг плана"),
}


def xp_to_level(xp: int) -> tuple[str, str, int, int]:
    """Возвращает (code, label, current_threshold, next_threshold)."""
    current = LEVELS[0]
    for lvl in LEVELS:
        if xp >= lvl[1]:
            current = lvl
    idx = LEVELS.index(current)
    next_threshold = LEVELS[idx + 1][1] if idx + 1 < len(LEVELS) else current[1]
    return current[0], current[2], current[1], next_threshold


def _now() -> datetime:
    return datetime.now(timezone.utc)


def update_streak(progress: UserProgress) -> None:
    now = _now()
    if progress.last_activity is None:
        progress.streak_days = 1
    else:
        delta = (now.date() - progress.last_activity.date()).days
        if delta == 0:
            return
        if delta == 1:
            progress.streak_days += 1
        else:
            progress.streak_days = 1
    progress.last_activity = now


def award_step(
    progress: UserProgress,
    skill: str,
    existing_achievements: set[str],
) -> list[str]:
    """Начисляет XP и возвращает список новых кодов достижений."""
    progress.xp += XP_PER_STEP
    update_streak(progress)

    unlocked: list[str] = []

    if not existing_achievements:
        unlocked.append("first_step")
    if skill == "sql" and "sql_ninja" not in existing_achievements:
        unlocked.append("sql_ninja")
    if skill == "python" and "pythonista" not in existing_achievements:
        unlocked.append("pythonista")
    if progress.streak_days >= 7 and "streak_7" not in existing_achievements:
        unlocked.append("streak_7")

    code, _, _, _ = xp_to_level(progress.xp)
    progress.level = code
    return unlocked


def make_achievement(user_id: int, code: str) -> Achievement:
    return Achievement(user_id=user_id, code=code)