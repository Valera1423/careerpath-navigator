"""Клиент API «Работа России» с кэшем, ретраями и fallback-набором.

Документация: http://opendata.trudvsem.ru/api/v1/vacancies
Токен не требуется. При недоступности API возвращаем помеченный fallback.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.config import settings
from app.services import cache, metrics
from app.services.skills import extract_skills

logger = logging.getLogger(__name__)


@dataclass
class Vacancy:
    id: str
    title: str
    company: str
    region: str
    salary: str | None
    url: str | None
    published_at: str | None
    skills: set[str] = field(default_factory=set)
    raw_text: str = ""


# --- ТЕСТОВЫЕ ДАННЫЕ (используются только если API недоступен) ---------------
FALLBACK_VACANCIES: list[dict[str, Any]] = [
    {
        "id": "test-analyst-1",
        "job-name": "Аналитик данных (стажёр)",
        "company": {"name": "Тестовая компания «Альфа»"},
        "region": {"name": "Москва"},
        "salary": {"from": 60000, "to": 80000, "currency": "руб."},
        "vac_url": "https://trudvsem.ru/vacancy/card/test-analyst-1",
        "duty": "Сбор и анализ данных, построение отчётов. SQL, Excel, Python, статистика.",
    },
    {
        "id": "test-backend-1",
        "job-name": "Python-разработчик (junior)",
        "company": {"name": "Тестовая компания «Бета»"},
        "region": {"name": "Санкт-Петербург"},
        "salary": {"from": 80000, "to": 120000, "currency": "руб."},
        "vac_url": "https://trudvsem.ru/vacancy/card/test-backend-1",
        "duty": "REST API на FastAPI, PostgreSQL, Docker, Git, Linux.",
    },
    {
        "id": "test-frontend-1",
        "job-name": "Frontend-разработчик (React)",
        "company": {"name": "Тестовая компания «Гамма»"},
        "region": {"name": "Москва"},
        "salary": None,
        "vac_url": "https://trudvsem.ru/vacancy/card/test-frontend-1",
        "duty": "Вёрстка HTML/CSS, JavaScript/TypeScript, React, Git, REST API.",
    },
]
# -----------------------------------------------------------------------------


def _format_salary(raw: Any) -> str | None:
    if not isinstance(raw, dict):
        return None
    lo, hi, cur = raw.get("from"), raw.get("to"), raw.get("currency") or "руб."
    if lo and hi:
        return f"{lo}–{hi} {cur}"
    if lo:
        return f"от {lo} {cur}"
    if hi:
        return f"до {hi} {cur}"
    return None


def _parse_vacancy(node: dict[str, Any]) -> Vacancy | None:
    v = node.get("vacancy") or node
    title = v.get("job-name") or v.get("job_name") or ""
    if not title:
        return None

    text_parts = [
        title,
        str(v.get("duty") or ""),
        str(v.get("requirements") or ""),
        str(v.get("qualification") or ""),
        str(v.get("education") or ""),
    ]
    raw_text = " ".join(text_parts)

    return Vacancy(
        id=str(v.get("id") or v.get("vacancy_id") or title),
        title=title.strip(),
        company=(v.get("company") or {}).get("name") or "Не указана",
        region=(v.get("region") or {}).get("name") or "Не указан",
        salary=_format_salary(v.get("salary")),
        url=v.get("vac_url") or v.get("vacancy-url") or v.get("url"),
        published_at=v.get("creation-date") or v.get("date"),
        skills=extract_skills(raw_text),
        raw_text=raw_text,
    )


async def _fetch_from_api(
    text: str, region_code: str | None, limit: int
) -> list[Vacancy]:
    params: dict[str, Any] = {"text": text, "limit": limit, "offset": 0}
    if region_code:
        params["regionCode"] = region_code

    url = f"{settings.trudvsem_base_url}/vacancies"
    last_error: Exception | None = None

    for attempt in range(settings.trudvsem_retries + 1):
        try:
            with metrics.TRUDVSEM_LATENCY.time():
                async with httpx.AsyncClient(timeout=settings.trudvsem_timeout) as client:
                    resp = await client.get(
                        url, params=params, headers={"Accept": "application/json"}
                    )
                    resp.raise_for_status()
                    payload = resp.json()

            nodes = payload.get("vacancies") or []
            metrics.TRUDVSEM_REQUESTS.labels(status="ok").inc()
            return [pv for node in nodes if (pv := _parse_vacancy(node))]
        except httpx.TimeoutException as exc:
            metrics.TRUDVSEM_REQUESTS.labels(status="timeout").inc()
            last_error = exc
            logger.warning("Trudvsem timeout, попытка %s", attempt + 1)
            await asyncio.sleep(0.6 * (attempt + 1))
        except Exception as exc:  # noqa: BLE001
            metrics.TRUDVSEM_REQUESTS.labels(status="error").inc()
            last_error = exc
            logger.warning("Trudvsem ошибка, попытка %s: %s", attempt + 1, exc)
            await asyncio.sleep(0.6 * (attempt + 1))

    if last_error:
        logger.error("Trudvsem недоступен: %s", last_error)
    return []


async def fetch_vacancies(
    text: str,
    region_code: str | None = None,
    limit: int = 50,
) -> tuple[list[Vacancy], str]:
    """Возвращает (вакансии, источник). Источник: 'trudvsem' | 'fallback'."""
    cached = cache.get("trudvsem", text, region_code, limit)
    if cached is not None:
        metrics.CACHE_HITS.inc()
        return cached

    metrics.CACHE_MISSES.inc()
    parsed = await _fetch_from_api(text, region_code, limit)

    if parsed:
        result = (parsed, "trudvsem")
        cache.put("trudvsem", text, region_code, limit, value=result)
        return result

    metrics.FALLBACK_SERVED.inc()
    fallback = [pv for node in FALLBACK_VACANCIES if (pv := _parse_vacancy(node))]
    return fallback, "fallback"