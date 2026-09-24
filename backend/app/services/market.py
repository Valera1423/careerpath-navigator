"""Аналитика рынка: тренды, зарплаты, топ-компании."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import VacancyCache


def _parse_salary(s: str | None) -> int | None:
    if not s:
        return None
    nums = [int(n) for n in re.findall(r"\d+", s.replace(" ", ""))]
    return sum(nums) // len(nums) if nums else None


def market_trends(
    db: Session,
    position: str,
    region: str | None = None,
    days: int = 30,
) -> dict:
    threshold = datetime.now(timezone.utc) - timedelta(days=days)

    rows = db.scalars(
        select(VacancyCache).where(VacancyCache.created_at >= threshold)
    ).all()

    skill_counter: Counter[str] = Counter()
    company_counter: Counter[str] = Counter()
    salary_buckets: dict[str, list[int]] = defaultdict(list)

    pos_lower = position.lower()
    for row in rows:
        for v in row.payload:
            title = (v.get("title") or "").lower()
            raw = (v.get("raw_text") or "").lower()
            if pos_lower not in title and pos_lower not in raw:
                continue
            for skill in v.get("skills", []):
                skill_counter[skill] += 1
            company = v.get("company") or "—"
            company_counter[company] += 1
            sal = _parse_salary(v.get("salary"))
            if sal:
                salary_buckets[region or "all"].append(sal)

    total = sum(skill_counter.values()) or 1
    top_skills = [
        {"skill": s, "count": c, "share": round(c / total, 3)}
        for s, c in skill_counter.most_common(10)
    ]

    salaries = salary_buckets.get(region or "all", [])
    salary_stats = {
        "min": min(salaries) if salaries else None,
        "max": max(salaries) if salaries else None,
        "avg": int(sum(salaries) / len(salaries)) if salaries else None,
        "sample": len(salaries),
    }

    return {
        "period_days": days,
        "vacancies_analyzed": len(rows),
        "top_skills": top_skills,
        "top_companies": [
            {"company": c, "vacancies": n}
            for c, n in company_counter.most_common(5)
        ],
        "salaries": salary_stats,
    }