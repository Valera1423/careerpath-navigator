"""Клиент MAX Bot API (platform-api2.max.ru).

Ограничения платформы:
- 30 запросов/сек на весь API
- 2 запроса/сек на один диалог/чат/канал
- токен передаётся в заголовке Authorization, без Bearer

Сертификат MAX подписан Russian Trusted Root CA (Минцифры) —
он установлен в контейнере через Dockerfile. На случай запуска вне
контейнера оставлен fallback на certifi.
"""
from __future__ import annotations

import asyncio
import logging
import ssl
import time
from collections import defaultdict
from typing import Any

import certifi
import httpx

logger = logging.getLogger(__name__)

MAX_API_BASE = "https://platform-api2.max.ru"


def _make_ssl_context() -> ssl.SSLContext:
    """SSL-контекст с системными CA + certifi как резервом."""
    ctx = ssl.create_default_context(cafile=certifi.where())
    # Системный store (куда Dockerfile положил russian-trusted-ca)
    ctx.load_default_certs()
    return ctx


def _make_client(token: str) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=MAX_API_BASE,
        headers={"Authorization": token},
        timeout=15.0,
        verify=_make_ssl_context(),
    )


def text_button(text: str) -> dict[str, Any]:
    """Простая кнопка, которая отправит текст как обычное сообщение."""
    return {"type": "message", "text": text}


def webapp_button(text: str, url: str) -> dict[str, Any]:
    """Кнопка, открывающая Web App (мини-приложение)."""
    return {"type": "web_app", "text": text, "web_app": {"url": url}}


def link_button(text: str, url: str) -> dict[str, Any]:
    return {"type": "link", "text": text, "url": url}


def keyboard(rows: list[list[dict[str, Any]]]) -> dict[str, Any]:
    """Собирает inline-клавиатуру из рядов кнопок."""
    return {"type": "inline_keyboard", "payload": {"buttons": rows}}


class MaxApiClient:
    def __init__(self, token: str) -> None:
        self._token = token
        self._client = _make_client(token)
        self._chat_locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._last_send: dict[int, float] = defaultdict(float)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        attachments: list[dict[str, Any]] | None = None,
    ) -> None:
        """Отправляет сообщение в чат с троттлингом 2 rps на чат."""
        async with self._chat_locks[chat_id]:
            elapsed = time.monotonic() - self._last_send[chat_id]
            if elapsed < 0.5:
                await asyncio.sleep(0.5 - elapsed)

            body: dict[str, Any] = {"chat_id": chat_id, "text": text}
            if attachments:
                body["attachments"] = attachments

            for attempt in range(3):
                resp = await self._client.post("/messages", json=body)
                if resp.status_code == 429:
                    await asyncio.sleep(2**attempt)
                    continue
                if resp.status_code >= 400:
                    logger.warning(
                        "MAX API %s: %s",
                        resp.status_code,
                        resp.text[:200],
                    )
                resp.raise_for_status()
                self._last_send[chat_id] = time.monotonic()
                return

            raise RuntimeError(
                "MAX API: не удалось отправить сообщение после 3 попыток"
            )

    async def send_keyboard(
        self,
        chat_id: int,
        text: str,
        rows: list[list[dict[str, Any]]],
    ) -> None:
        """Отправляет сообщение с inline-клавиатурой."""
        await self.send_message(
            chat_id=chat_id,
            text=text,
            attachments=[keyboard(rows)],
        )

    async def aclose(self) -> None:
        await self._client.aclose()


async def register_webhook(webhook_url: str, secret: str, token: str) -> dict:
    """Регистрирует webhook-подписку в MAX.

    Использует тот же SSL-контекст, что и MaxApiClient.
    """
    async with _make_client(token) as client:
        # Снимаем старые подписки, чтобы не дублировались
        try:
            existing = await client.get("/subscriptions")
            if existing.status_code == 200:
                for sub in existing.json().get("subscriptions", []):
                    await client.delete(f"/subscriptions/{sub['url']}")
        except Exception:  # noqa: BLE001
            logger.debug("Не удалось снять старые подписки", exc_info=True)

        resp = await client.post(
            "/subscriptions",
            json={
                "url": webhook_url,
                "update_types": ["message_created", "bot_started"],
                "secret": secret,
            },
        )
        resp.raise_for_status()
        return resp.json()