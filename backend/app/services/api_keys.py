"""Генерация и проверка API-ключей для работодателей."""
from __future__ import annotations

import secrets

import bcrypt


def generate_api_key() -> tuple[str, str]:
    """Возвращает (raw_key, hash). raw_key показывается ОДИН раз."""
    raw = f"cp_{secrets.token_urlsafe(32)}"
    hashed = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()
    return raw, hashed


def verify_api_key(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False