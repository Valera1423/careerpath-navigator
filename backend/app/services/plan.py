"""Генерация плана развития из gap-анализа."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.schemas import SkillGapItem

# Известные материалы. Ключи — канонические имена навыков из skills.yaml
RESOURCES: dict[str, tuple[str, str | None]] = {
    "sql": ("Интерактивный тренажёр по SQL", "https://stepik.org/course/63054"),
    "python": ("Python для начинающих", "https://stepik.org/course/67"),
    "excel": ("Excel для анализа данных", "https://stepik.org/course/126"),
    "statistics": ("Основы статистики", "https://stepik.org/course/76"),
    "power_bi": ("Power BI: с нуля", "https://learn.microsoft.com/ru-ru/power-bi/"),
    "pandas": ("Pandas за 10 минут", "https://pandas.pydata.org/docs/user_guide/10min.html"),
    "product_analytics": ("Продуктовая аналитика", "https://stepik.org/course/118265"),
    "javascript": ("Современный учебник JavaScript", "https://learn.javascript.ru/"),
    "typescript": ("TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html"),
    "react": ("React: официальный туториал", "https://react.dev/learn"),
    "html_css": ("HTML Academy: базовый курс", "https://htmlacademy.ru/courses/basic-html-css"),
    "figma": ("Figma для начинающих", "https://www.figma.com/resources/learn-design/"),
    "ui_ux": ("UX/UI дизайн", "https://stepik.org/course/92056"),
    "docker": ("Docker: getting started", "https://docs.docker.com/get-started/"),
    "git": ("Pro Git (книга, RU)", "https://git-scm.com/book/ru/v2"),
    "linux": ("Введение в Linux", "https://stepik.org/course/73"),
    "postgresql": ("PostgreSQL Tutorial", "https://www.postgresqltutorial.com/"),
    "rest_api": ("REST API: дизайн", "https://restfulapi.net/"),
    "communication": ("Коммуникация в команде", "https://stepik.org/course/108967"),
    "english": ("Английский для IT", "https://puzzle-english.com/"),
    "project_management": ("Управление проектами", "https://stepik.org/course/66704"),
    "agile": ("Agile и Scrum", "https://scrumguides.org/scrum-guide.html"),
    "jira": ("Jira для команд", "https://www.atlassian.com/ru/software/jira/guides"),
}

_PRIORITY_OFFSET = {"critical": 0, "important": 7, "nice-to-have": 21}


def _resource_for(skill: str) -> tuple[str, str | None]:
    return RESOURCES.get(skill) or (
        f"Курс по «{skill.replace('_', ' ')}»",
        None,
    )


def build_plan(missing: list[SkillGapItem]) -> list[dict]:
    """Превращает список недостающих навыков в шаги плана.

    Возвращает list[dict], готовый для PlanStep(**raw).
    Критичные навыки идут первыми, дедлайны распределены по неделям.
    """
    if not missing:
        return []

    now = datetime.now(timezone.utc)
    week = timedelta(days=7)

    # Сначала сортируем: critical → important → nice-to-have, затем по demand
    ordered = sorted(
        missing,
        key=lambda i: (_PRIORITY_OFFSET.get(i.importance, 99), -i.demand, i.skill),
    )

    steps: list[dict] = []
    for idx, item in enumerate(ordered):
        title, url = _resource_for(item.skill)
        share_pct = int(round(item.demand_share * 100))
        steps.append(
            {
                "order_index": idx,
                "skill": item.skill,
                "title": title,
                "description": (
                    f"Навык встречается в {share_pct}% вакансий по вашей цели. "
                    f"Важность: {item.importance}."
                ),
                "kind": "course",
                "resource_url": url,
                "due_date": now + week * (idx + 1),
                "depends_on": [],
            }
        )
    return steps