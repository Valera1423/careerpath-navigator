"""Расчёт gap-анализа: чего не хватает пользователю до целевой роли."""
from __future__ import annotations

from collections import Counter

from app.schemas import SkillGapItem, SkillGapResponse
from app.services.skills import core_skills_for, normalize_skill
from app.services.trudvsem import Vacancy


def _importance(demand: int, analyzed: int) -> str:
    if analyzed <= 0:
        return "important"
    share = demand / analyzed
    if demand >= 3 or share >= 0.30:
        return "critical"
    if demand >= 1 or share >= 0.15:
        return "important"
    return "nice-to-have"


def compute_gap(
    position: str,
    region: str | None,
    user_skills: list[str],
    vacancies: list[Vacancy],
    source: str,
) -> SkillGapResponse:
    """Считает покрытие навыков пользователя относительно вакансий и роли.

    Всегда возвращает SkillGapResponse — даже если вакансий не нашлось,
    тогда используются core-навыки роли из roles.yaml.
    """
    user_set = {normalize_skill(s) for s in user_skills if s and s.strip()}

    counter: Counter[str] = Counter()
    for v in vacancies:
        for skill in v.skills:
            counter[skill] += 1

    # Core-навыки роли — всегда в списке, чтобы план не был пустым
    core = core_skills_for(position)
    for skill in core:
        counter.setdefault(normalize_skill(skill), 0)

    analyzed = max(len(vacancies), 1)

    matched: list[SkillGapItem] = []
    missing: list[SkillGapItem] = []

    for skill, demand in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
        item = SkillGapItem(
            skill=skill,
            demand=demand,
            demand_share=round(demand / analyzed, 3),
            importance=_importance(demand, analyzed),  # type: ignore[arg-type]
        )
        (matched if skill in user_set else missing).append(item)

    # Readiness = доля совпавших от общего числа релевантных навыков
    total = len(matched) + len(missing)
    readiness = int(round(100 * len(matched) / total)) if total else 0

    return SkillGapResponse(
        position=position,
        region=region,
        vacancies_analyzed=len(vacancies),
        source="trudvsem" if source == "trudvsem" else "fallback",
        matched=matched,
        missing=missing,
        readiness_score=readiness,
    )