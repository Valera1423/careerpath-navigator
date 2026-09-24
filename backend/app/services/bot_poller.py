"""Long Polling бот для MAX.

Запускается отдельным процессом, опрашивает MAX на новые сообщения.
Не требует публичного HTTPS, туннелей и вебхуков.

Запуск: python -m app.services.bot_poller
"""
from __future__ import annotations

import asyncio
import json
import logging

import httpx
from maxapi import Bot, Dispatcher, F
from maxapi.filters.command import CommandStart
from maxapi.types import BotStarted, MessageCreated

from app.config import settings
from app.database import SessionLocal
from app.services.bot_commands import handle_update
from app.services.max_api import MAX_API_BASE, _make_ssl_context

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

if not settings.max_bot_token:
    raise SystemExit("MAX_BOT_TOKEN не задан — бот не запустится")

bot = Bot(token=settings.max_bot_token)
dp = Dispatcher()


# ---------------------------------------------------------------------------
# Адаптер: делает maxapi.Bot совместимым с интерфейсом MaxApiClient
# ---------------------------------------------------------------------------
class MaxApiAdapter:
    """Мост между maxapi.Bot и ожиданиями handle_update.

    Отправляет сообщения напрямую через MAX Bot API (httpx).
    Если attachments (inline-клавиатура) не принимаются — отправляет
    только текст, чтобы бот не молчал.
    """

    def __init__(self, token: str) -> None:
        self._token = token
        self._ssl = _make_ssl_context()

    async def _post(
        self,
        path: str,
        body: dict,
        params: dict | None = None,
    ) -> httpx.Response:
        async with httpx.AsyncClient(
            base_url=MAX_API_BASE,
            headers={"Authorization": self._token},
            timeout=15.0,
            verify=self._ssl,
        ) as client:
            return await client.post(path, json=body, params=params)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        attachments: list[dict] | None = None,
    ) -> None:
        """Отправляет сообщение. chat_id == user_id для личных диалогов."""
        body: dict = {"text": text}
        if attachments:
            body["attachments"] = attachments

        resp = await self._post("/messages", body, params={"user_id": chat_id})

        if resp.status_code >= 400:
            logger.warning(
                "MAX API %s: %s | body=%s",
                resp.status_code,
                resp.text[:300],
                json.dumps(body, ensure_ascii=False)[:400],
            )
        resp.raise_for_status()

    async def send_keyboard(
        self,
        chat_id: int,
        text: str,
        rows: list[list[dict]],
    ) -> None:
        """Отправляет сообщение с inline-клавиатурой.

        Пробует несколько форматов; если ни один не принят — fallback
        на текст без кнопок (бот не должен молчать).
        """
        # Вариант 1: attachments с payload.buttons (по документации)
        variants: list[list[dict]] = [
            [{"type": "inline_keyboard", "payload": {"buttons": rows}}],
            [{"type": "inline_keyboard", "buttons": rows}],
            [{"type": "keyboard", "payload": {"buttons": rows}}],
        ]

        for variant in variants:
            try:
                await self.send_message(chat_id, text, attachments=variant)
                return  # успех — выходим
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 400:
                    raise
                logger.debug(
                    "Формат не принят (%s), пробуем следующий",
                    json.dumps(variant, ensure_ascii=False)[:200],
                )
                continue

        # Если ни один формат не прошёл — отправляем только текст
        logger.warning("Ни один формат клавиатуры не принят, отправляю текст")
        await self.send_message(chat_id, text)

    async def aclose(self) -> None:
        pass


_adapter = MaxApiAdapter(settings.max_bot_token)


# ---------------------------------------------------------------------------
# Обработчики событий
# ---------------------------------------------------------------------------

async def _handle(chat_id: int, user_id: str, text: str) -> None:
    logger.info("Получено: chat=%s user=%s text=%r", chat_id, user_id, text[:100])
    webapp_url = (settings.webapp_url or "").strip() or "https://max.ru"

    with SessionLocal() as db:
        try:
            await handle_update(
                db=db,
                client=_adapter,
                chat_id=int(user_id),  # личный диалог → user_id
                user_id=user_id,
                raw_text=text,
                webapp_url=webapp_url,
            )
            logger.info("handle_update отработал успешно")
        except Exception as exc:
            logger.exception("Ошибка handle_update: %s", exc)


@dp.bot_started()
async def on_bot_started(event: BotStarted) -> None:
    await _handle(
        chat_id=event.chat_id,
        user_id=str(event.user.user_id) if event.user else "",
        text="/start",
    )


@dp.message_created(CommandStart())
async def on_start_command(event: MessageCreated) -> None:
    await _handle(
        chat_id=event.message.recipient.chat_id,
        user_id=str(event.message.sender.user_id),
        text="/start",
    )


@dp.message_created(F.message.body.text)
async def on_any_message(event: MessageCreated) -> None:
    await _handle(
        chat_id=event.message.recipient.chat_id,
        user_id=str(event.message.sender.user_id),
        text=event.message.body.text,
    )


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

async def main() -> None:
    logger.info("Запускаем Long Polling...")
    try:
        await bot.delete_webhook()
        logger.info("Вебхуки сняты")
    except Exception as exc:
        logger.warning("delete_webhook не сработал: %s", exc)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())