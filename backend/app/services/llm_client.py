"""Обёртка над LLM. Работает через OpenAI-совместимый API (в т.ч. MAX GPT).

Если LLM_API_KEY не задан — методы возвращают None, а вызывающий код
использует шаблонный fallback. Это гарантирует работу демо без сети.
"""
from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class LlmClient:
    def __init__(self) -> None:
        self._enabled = bool(settings.llm_api_key)

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 400,
        temperature: float = 0.4,
    ) -> str | None:
        if not self._enabled:
            return None

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    f"{settings.llm_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.llm_model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM недоступна: %s", exc)
            return None


llm_client = LlmClient()