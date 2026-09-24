"""Регистрация webhook-подписки в MAX.

Запуск:
    docker compose exec backend python -m app.bot.register

Требует переменные окружения:
    MAX_BOT_TOKEN      — токен бота
    WEBHOOK_URL        — публичный HTTPS-адрес /webhook/max
    MAX_WEBHOOK_SECRET — секрет подписи (любая строка)
"""
from __future__ import annotations

import asyncio
import logging
import sys

from app.config import settings
from app.services.max_api import register_webhook

logger = logging.getLogger(__name__)


async def main() -> int:
    if not settings.max_bot_token:
        print("ERROR: MAX_BOT_TOKEN не задан", file=sys.stderr)
        return 1
    if not settings.webhook_url:
        print("ERROR: WEBHOOK_URL не задан", file=sys.stderr)
        return 1

    print(f"Регистрирую webhook: {settings.webhook_url}")
    try:
        result = await register_webhook(
            webhook_url=settings.webhook_url,
            secret=settings.max_webhook_secret,
            token=settings.max_bot_token,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print("Webhook зарегистрирован:", result)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(asyncio.run(main()))