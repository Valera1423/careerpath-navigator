"""Обработка команд чат-бота MAX.

Бот — «входная дверь» в мини-приложение:
- приветствие + кнопка «Открыть CareerPath Navigator»
- быстрый доступ к плану и прогрессу
- свободный текст уходит в AI-коуча (LLM/шаблон)
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PlanStep, User, UserProgress
from app.services.coach import answer, build_context
from app.services.gamification import xp_to_level
from app.services.max_api import (
    MaxApiClient,
    link_button,
    webapp_button,
)

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "Привет! Я CareerPath Navigator — помогу построить карьерный план, "
    "проверить навыки и подготовиться к собеседованию.\n\n"
    "Открой мини-приложение, чтобы пройти онбординг и получить план:\n"
    "• 📋 План — шаги развития\n"
    "• 🎯 Симулятор — прожить день аналитика\n"
    "• 🎤 Интервью — тренировка STAR-ответов\n\n"
    "Свободные вопросы тоже можно задавать мне — отвечу как карьерный коуч."
)

HELP_TEXT = (
    "Что я умею:\n"
    "/start — открыть мини-приложение\n"
    "/plan — прогресс по плану развития\n"
    "/progress — XP, уровень, streak\n"
    "/help — это сообщение\n\n"
    "Любой другой текст — вопрос карьерному коучу."
)


def _webapp_url(base: str) -> str:
    return base.rstrip("/") + "/"


def _start_rows(webapp_url: str) -> list[list[dict]]:
    return [
        [webapp_button("🚀 Открыть CareerPath Navigator", webapp_url)],
        [link_button("ℹ️ О платформе MAX", "https://max.ru")],
    ]


def _plan_rows(webapp_url: str) -> list[list[dict]]:
    return [
        [webapp_button("📋 Открыть план", webapp_url)],
        [webapp_button("🎯 Симулятор дня", webapp_url)],
    ]


def _progress_rows(webapp_url: str) -> list[list[dict]]:
    return [
        [webapp_button("🏆 Открыть лидерборд", webapp_url)],
    ]


def _handle_start(db: Session, user: User | None, webapp_url: str) -> tuple[str, list]:
    if user is None:
        text = (
            "Привет! Ты ещё не проходил онбординг в CareerPath Navigator.\n"
            "Открой мини-приложение — это займёт 1 минуту, и я построю "
            "твой персональный план развития."
        )
    else:
        text = WELCOME_TEXT
    return text, _start_rows(webapp_url)


def _handle_plan(db: Session, user: User, webapp_url: str) -> tuple[str, list]:
    steps = list(
        db.scalars(
            select(PlanStep)
            .where(PlanStep.user_id == user.id)
            .order_by(PlanStep.order_index)
        )
    )
    if not steps:
        return (
            f"План для роли «{user.desired_position}» пока пуст. "
            "Открой мини-приложение и нажми «Пересчитать план».",
            _plan_rows(webapp_url),
        )

    done = sum(1 for s in steps if s.is_done)
    next_step = next((s for s in steps if not s.is_done), None)
    pct = int(round(100 * done / len(steps)))

    text = f"📋 Прогресс: {done}/{len(steps)} ({pct}%)\n"
    if next_step:
        text += f"\nСледующий шаг: *{next_step.title}*\n_{next_step.description}_"
    else:
        text += "\n🎉 Все шаги выполнены — можно переходить к симулятору!"
    return text, _plan_rows(webapp_url)


def _handle_progress(db: Session, user: User, webapp_url: str) -> tuple[str, list]:
    progress = db.scalar(
        select(UserProgress).where(UserProgress.user_id == user.id)
    )
    xp = progress.xp if progress else 0
    streak = progress.streak_days if progress else 0

    _, label, current, next_threshold = xp_to_level(xp)
    if next_threshold > current:
        pct = int(round(100 * (xp - current) / (next_threshold - current)))
        tail = f" · до следующего: {pct}%"
    else:
        tail = " · максимум"

    text = (
        f"🏅 Уровень: *{label}*\n"
        f"XP: {xp}{tail}\n"
        f"🔥 Streak: {streak} дн."
    )
    return text, _progress_rows(webapp_url)


async def handle_update(
    db: Session,
    client: MaxApiClient,
    chat_id: int,
    user_id: str,
    raw_text: str,
    webapp_url: str,
) -> None:
    """Обрабатывает одно входящее сообщение от MAX."""
    text = (raw_text or "").strip()
    command = text.split("@", 1)[0].lower() if text.startswith("/") else ""

    user = db.query(User).filter(User.max_user_id == user_id).first()

    try:
        if command in ("/start", "/begin"):
            reply, rows = _handle_start(db, user, webapp_url)
        elif command == "/help":
            reply, rows = HELP_TEXT, _start_rows(webapp_url)
        elif command == "/plan":
            if user is None:
                reply, rows = _handle_start(db, None, webapp_url)
            else:
                reply, rows = _handle_plan(db, user, webapp_url)
        elif command == "/progress":
            if user is None:
                reply, rows = _handle_start(db, None, webapp_url)
            else:
                reply, rows = _handle_progress(db, user, webapp_url)
        elif user is None:
            reply, rows = _handle_start(db, None, webapp_url)
        else:
            # Свободный текст → AI-коуч
            steps = list(
                db.query(PlanStep).filter(PlanStep.user_id == user.id).all()
            )
            ctx = await build_context(user, steps)
            reply = answer(text, ctx)
            rows = _plan_rows(webapp_url)

        await client.send_keyboard(chat_id=chat_id, text=reply, rows=rows)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Ошибка обработки команды %r: %s", command, exc)
        try:
            await client.send_message(
                chat_id=chat_id,
                text="Извини, что-то пошло не так. Попробуй ещё раз через минуту.",
            )
        except Exception:  # noqa: BLE001
            logger.exception("Не удалось отправить сообщение об ошибке")