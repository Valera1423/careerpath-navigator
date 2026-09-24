"""Вебхук MAX Bot API.

Принимает события от MAX, логирует payload и передаёт в bot_commands.
"""
from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.config import settings
from app.database import SessionLocal
from app.services.bot_commands import handle_update
from app.services.max_api import MaxApiClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


def _webapp_url() -> str:
    url = (settings.webapp_url or "").strip()
    if url:
        return url
    if settings.webhook_url:
        return settings.webhook_url.rsplit("/webhook", 1)[0]
    return "https://max.ru"


def _extract_update_type(payload: dict) -> str:
    """MAX в разных версиях API использует разные ключи."""
    for key in ("update_type", "type", "updateType", "event"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def _extract_message(payload: dict) -> dict:
    for key in ("message", "data", "payload"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _extract_text(message: dict) -> str:
    # Формат: {"body": {"text": "..."}}
    body = message.get("body")
    if isinstance(body, dict):
        for key in ("text", "body", "content"):
            value = body.get(key)
            if isinstance(value, str):
                return value
    # Fallback: плоская структура
    for key in ("text", "body", "content", "message"):
        value = message.get(key)
        if isinstance(value, str):
            return value
    return ""


def _extract_user_id(message: dict) -> str:
    for key in ("sender", "from", "user", "author"):
        sender = message.get(key)
        if isinstance(sender, dict):
            for uid_key in ("user_id", "id", "userId"):
                value = sender.get(uid_key)
                if value is not None:
                    return str(value)
    return ""


def _extract_chat_id(message: dict) -> int | None:
    for key in ("recipient", "chat", "to", "conversation"):
        recipient = message.get(key)
        if isinstance(recipient, dict):
            for cid_key in ("chat_id", "id", "chatId"):
                value = recipient.get(cid_key)
                if value is not None:
                    try:
                        return int(value)
                    except (TypeError, ValueError):
                        continue
    # Fallback: chat_id на верхнем уровне message
    for cid_key in ("chat_id", "chatId"):
        value = message.get(cid_key)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    return None


@router.post("/max")
async def max_webhook(
    request: Request,
    payload: dict,
    x_max_bot_api_secret: str | None = Header(
        default=None, alias="X-Max-Bot-Api-Secret"
    ),
) -> dict:
    # Логируем ВСЁ, что приходит — понадобится для отладки
    raw = json.dumps(payload, ensure_ascii=False)
    logger.info("=== WEBHOOK INCOMING ===")
    logger.info("secret header: %r (expected: %r)", x_max_bot_api_secret, settings.max_webhook_secret)
    logger.info("content-type: %r", request.headers.get("content-type"))
    logger.info("payload: %s", raw[:3000])

    if x_max_bot_api_secret != settings.max_webhook_secret:
        logger.warning("Webhook: неверный секрет")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid secret")

    update_type = _extract_update_type(payload)
    logger.info("update_type = %r", update_type)

    if update_type not in ("message_created", "bot_started"):
        logger.info("Webhook: пропускаем тип %r", update_type)
        return {"ok": True}

    if not settings.max_bot_token:
        logger.warning("Webhook: MAX_BOT_TOKEN пуст, ответ невозможен")
        return {"ok": True}

    message = _extract_message(payload)
    text = _extract_text(message).strip()
    user_id = _extract_user_id(message)
    chat_id = _extract_chat_id(message)

    logger.info(
        "extracted: user_id=%r chat_id=%r text=%r",
        user_id, chat_id, text[:100] if text else "",
    )

    if update_type == "bot_started":
        text = "/start"
    elif not text:
        logger.info("Webhook: пустой текст, пропускаем")
        return {"ok": True}

    if not chat_id:
        logger.warning("Webhook: не удалось извлечь chat_id")
        return {"ok": True}

    webapp_url = _webapp_url()
    logger.info("webapp_url = %s", webapp_url)

    client = MaxApiClient(token=settings.max_bot_token)
    try:
        with SessionLocal() as db:
            await handle_update(
                db=db,
                client=client,
                chat_id=chat_id,
                user_id=user_id,
                raw_text=text,
                webapp_url=webapp_url,
            )
        logger.info("Webhook: handle_update завершён успешно")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Webhook: ошибка в handle_update: %s", exc)
    finally:
        await client.aclose()

    return {"ok": True}