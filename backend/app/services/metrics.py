"""Кастомные метрики Prometheus."""
from __future__ import annotations

from prometheus_client import Counter, Histogram

TRUDVSEM_REQUESTS = Counter(
    "trudvsem_requests_total",
    "Запросы к API «Работа России»",
    ["status"],  # ok | error | timeout
)

TRUDVSEM_LATENCY = Histogram(
    "trudvsem_latency_seconds",
    "Латентность запросов к API «Работа России»",
)

FALLBACK_SERVED = Counter(
    "trudvsem_fallback_total",
    "Отдано fallback-наборов вакансий",
)

CACHE_HITS = Counter(
    "vacancies_cache_hits_total",
    "Попадания в кэш вакансий",
)

CACHE_MISSES = Counter(
    "vacancies_cache_misses_total",
    "Промахи кэша вакансий",
)