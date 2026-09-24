"""Прогноз спроса на навыки на N месяцев вперёд.

Использует линейную регрессию по историческим данным (кэш вакансий).
Для MVP достаточно 3–6 месяцев истории; при меньшем объёме возвращаем
"тренд = stable" без численного прогноза.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import VacancyCache


def _month_key(dt: datetime) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"


def forecast_skills(
    db: Session,
    position: str,
    horizon_months: int = 6,
    history_months: int = 6,
) -> list[dict]:
    threshold = datetime.now(timezone.utc) - timedelta(days=history_months * 31)
    rows = db.scalars(
        select(VacancyCache).where(VacancyCache.created_at >= threshold)
    ).all()

    monthly: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    pos_lower = position.lower()

    for row in rows:
        mk = _month_key(row.created_at)
        for v in row.payload:
            title = (v.get("title") or "").lower()
            raw = (v.get("raw_text") or "").lower()
            if pos_lower not in title and pos_lower not in raw:
                continue
            for skill in v.get("skills", []):
                monthly[skill][mk] += 1

    result: list[dict] = []
    for skill, series in monthly.items():
        if len(series) < 3:
            continue
        sorted_months = sorted(series.keys())
        xs = list(range(len(sorted_months)))
        ys = [series[m] for m in sorted_months]

        try:
            import numpy as np

            coeffs = np.polyfit(xs, ys, 1)
            slope = float(coeffs[0])
            current = ys[-1]
            predicted = max(0, int(round(current + slope * horizon_months)))

            if slope > 0.5:
                trend = "growing"
            elif slope < -0.5:
                trend = "declining"
            else:
                trend = "stable"

            result.append(
                {
                    "skill": skill,
                    "current": current,
                    "predicted": predicted,
                    "trend": trend,
                    "change_pct": int(round(100 * slope * horizon_months / max(current, 1))),
                }
            )
        except Exception:  # noqa: BLE001
            continue

    result.sort(key=lambda r: -r["predicted"])
    return result[:10]