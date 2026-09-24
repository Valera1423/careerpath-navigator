"""Планировщик напоминаний по откликам.

Запуск (в отдельном контейнере/процессе):
    python -m app.services.scheduler

Раз в N минут проверяет applications с истёкшим remind_at и отправляет
пользователю напоминание в MAX, после чего очищает remind_at.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Application, User
from app.services.max_api import MaxApiClient

logger = logging.getLogger(__name__)

CHECK_INTERVAL_MINUTES = 15


def _reminder_text(app: Application) -> str:
    company = f" в «{app.company}»" if app.company else ""
    return (
        f"🔔 Напоминание о отклике\n\n"
        f"Вакансия: «{app.vacancy_title}»{company}.\n"
        f"Пора проверить статус — возможно, пора написать HR."
    )


async def send_due_reminders() -> None:
    """Один проход по БД: отправляет все «созревшие» напоминания."""
    if not settings.max_bot_token:
        logger.warning("MAX_BOT_TOKEN не задан — напоминания пропущены")
        return

    now = datetime.now(timezone.utc)
    client = MaxApiClient(token=settings.max_bot_token)
    sent = 0
    try:
        with SessionLocal() as db:
            due = list(
                db.scalars(
                    select(Application).where(
                        Application.remind_at.is_not(None),
                        Application.remind_at <= now,
                    )
                )
            )
            if not due:
                return

            for app in due:
                user = db.get(User, app.user_id)
                if user is None:
                    app.remind_at = None
                    continue

                # В MAX chat_id приватного чата == user_id
                try:
                    chat_id = int(user.max_user_id)
                except (TypeError, ValueError):
                    # dev-user-1 и подобные — отправлять некуда
                    app.remind_at = None
                    continue

                try:
                    await client.send_message(chat_id=chat_id, text=_reminder_text(app))
                    sent += 1
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Не удалось отправить напоминание user=%s: %s", chat_id, exc)
                    continue

                app.remind_at = None

            db.commit()

        if sent:
            logger.info("Отправлено напоминаний: %s", sent)
    finally:
        await client.aclose()


async def _main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_due_reminders,
        "interval",
        minutes=CHECK_INTERVAL_MINUTES,
        next_run_time=datetime.now(timezone.utc),  # сразу при старте
    )
    scheduler.start()
    logger.info("Планировщик напоминаний запущен (интервал: %s мин)", CHECK_INTERVAL_MINUTES)

    try:
        # Держим процесс живым
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(_main())