"""TTL-кэш с интерфейсом, совместимым с Redis.

Локальная реализация через cachetools. При масштабировании на несколько
инстансов достаточно заменить реализацию get/put на redis.asyncio,
не меняя вызывающий код.
"""
from __future__ import annotations

import logging
from typing import Any

from cachetools import TTLCache

from app.config import settings

logger = logging.getLogger(__name__)

# Размер 2048 записей × TTL из настроек
_cache: TTLCache[str, Any] = TTLCache(
    maxsize=2048,
    ttl=settings.cache_ttl_hours * 3600,
)


def _key(prefix: str, *parts: Any) -> str:
    return f"{prefix}:" + ":".join(str(p) for p in parts)


def get(prefix: str, *parts: Any) -> Any | None:
    key = _key(prefix, *parts)
    value = _cache.get(key)
    if value is not None:
        logger.debug("cache hit: %s", key)
    return value


def put(prefix: str, *parts: Any, value: Any) -> None:
    key = _key(prefix, *parts)
    _cache[key] = value
    logger.debug("cache put: %s", key)


def invalidate(prefix: str, *parts: Any) -> None:
    key = _key(prefix, *parts)
    _cache.pop(key, None)


def clear() -> None:
    _cache.clear()