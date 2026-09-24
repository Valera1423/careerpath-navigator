"""Проверка подписи initData от MAX Bridge.

Алгоритм:
1. initData — query-string (URL-encoded).
2. Убираем поле `hash`.
3. Сортируем оставшиеся пары key=value лексикографически, склеиваем через \\n.
4. secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token)
5. Ожидаемая подпись = HMAC_SHA256(key=secret_key, msg=data_check_string).hexdigest()
6. Сравниваем с hash через secrets.compare_digest.

TTL: 1 час (рекомендация MAX).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl

from fastapi import HTTPException, status

from app.config import settings

MAX_INIT_DATA_AGE = 3600


@dataclass(frozen=True)
class MaxUser:
    id: str
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


def _build_data_check_string(pairs: list[tuple[str, str]]) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(pairs) if k != "hash")


def _fallback_user(raw: str) -> MaxUser:
    for k, v in parse_qsl(raw, keep_blank_values=True):
        if k == "user_id":
            return MaxUser(id=v)
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Не удалось извлечь user в dev-режиме")


def verify_init_data(raw: str) -> MaxUser:
    if not raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData отсутствует")

    if not settings.max_bot_token:
        if settings.allow_insecure_init_data:
            return _fallback_user(raw)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "MAX_BOT_TOKEN не сконфигурирован",
        )

    pairs = parse_qsl(raw, keep_blank_values=True)
    received_hash = next((v for k, v in pairs if k == "hash"), None)
    if not received_hash:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "hash отсутствует")

    data_check_string = _build_data_check_string(pairs)
    secret = hmac.new(b"WebAppData", settings.max_bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, received_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверная подпись initData")

    auth_date = next((int(v) for k, v in pairs if k == "auth_date"), 0)
    if auth_date and time.time() - auth_date > MAX_INIT_DATA_AGE:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "initData устарел")

    user_json = next((v for k, v in pairs if k == "user"), None)
    if not user_json:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user отсутствует в initData")

    data = json.loads(user_json)
    return MaxUser(
        id=str(data["id"]),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        username=data.get("username"),
    )