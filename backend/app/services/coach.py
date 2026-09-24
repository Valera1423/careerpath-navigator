"""AI-коуч: персонализированные ответы на основе профиля."""
from __future__ import annotations

from dataclasses import dataclass

from app.models import PlanStep, User
from app.services.gap import compute_gap
from app.services.llm_client import llm_client
from app.services.trudvsem import fetch_vacancies


@dataclass
class CoachContext:
    desired_position: str
    skills: list[str]
    missing_skills: list[str]
    readiness_score: int
    plan_summary: str


async def build_context(user: User, steps: list[PlanStep]) -> CoachContext:
    vacancies, _ = await fetch_vacancies(text=user.desired_position, limit=30)
    gap = compute_gap(
        position=user.desired_position,
        region=user.region,
        user_skills=user.skills,
        vacancies=vacancies,
        source="trudvsem",
    )
    done = sum(1 for s in steps if s.is_done)
    return CoachContext(
        desired_position=user.desired_position,
        skills=user.skills,
        missing_skills=[i.skill for i in gap.missing[:5]],
        readiness_score=gap.readiness_score,
        plan_summary=f"{done}/{len(steps)} шагов выполнено",
    )


TEMPLATES: dict[str, str] = {
    "sql": (
        "SQL — базовый инструмент аналитика. Без него нельзя самостоятельно "
        "достать данные из базы, а значит — построить отчёт. В вакансиях на "
        "позицию «{position}» SQL встречается в {share}% случаев. Начните с "
        "«Интерактивного тренажёра по SQL» на Stepik — 60+ задач закроют базу "
        "за 2–3 недели."
    ),
    "python": (
        "Python для {position} — это автоматизация рутины и работа с данными. "
        "Вам не нужен «весь Python»: достаточно pandas, requests и основ ООП. "
        "Сделайте проект — парсер вакансий с выгрузкой в CSV."
    ),
    "statistics": (
        "Статистика нужна, чтобы отличать реальные изменения от случайных. "
        "Начните с A/B-тестов: сгенерируйте данные, посчитайте p-value, "
        "оформите вывод. Это стандартный вопрос на собеседовании."
    ),
    "power_bi": (
        "Power BI — это про визуализацию данных для бизнеса. Начните с "
        "подключения открытого датасета (например, Росстат) и постройте "
        "дашборд с 3–4 KPI. Скриншоты — в портфолио."
    ),
    "figma": (
        "Figma — стандарт для UI/UX. Достаточно освоить фреймы, компоненты "
        "и автолейауты. Сверстайте макет из 3 экранов мобильного приложения "
        "и добавьте кликабельный прототип."
    ),
    "docker": (
        "Docker нужен, чтобы «работало у всех одинаково». Начните с "
        "докеризации своего pet-проекта: Dockerfile + compose.yaml, "
        "приложение поднимается одной командой."
    ),
}

GENERIC_TEMPLATE = (
    "Навык «{skill}» встречается в {share}% вакансий на позицию «{position}». "
    "Рекомендую начать с профильного курса, а затем закрепить практикой: "
    "сделайте мини-проект и опубликуйте его на GitHub."
)


def _share_for(skill: str, missing: list[str]) -> int:
    idx = missing.index(skill) if skill in missing else len(missing)
    return max(30, 90 - idx * 15)


async def answer_async(question: str, ctx: CoachContext) -> str:
    """Пытается получить ответ от LLM, при неудаче — шаблон."""
    if llm_client.enabled:
        system = (
            "Ты — карьерный коуч для студентов и выпускников. Отвечай кратко "
            "(3–5 предложений), конкретно, ссылайся на навыки пользователя. "
            "Не выдумывай ссылки. Пиши на русском."
        )
        user_prompt = (
            f"Целевая должность: {ctx.desired_position}\n"
            f"Текущие навыки: {', '.join(ctx.skills) or '—'}\n"
            f"Не хватает: {', '.join(ctx.missing_skills) or '—'}\n"
            f"Готовность: {ctx.readiness_score}%\n"
            f"План: {ctx.plan_summary}\n\n"
            f"Вопрос: {question}"
        )
        reply = await llm_client.complete(system, user_prompt)
        if reply:
            return reply

    return answer(question, ctx)


def answer(question: str, ctx: CoachContext) -> str:
    """Шаблонный ответ (fallback)."""
    q = question.lower()
    for skill in ctx.missing_skills:
        if skill.replace("_", " ") in q or skill in q:
            share = _share_for(skill, ctx.missing_skills)
            template = TEMPLATES.get(skill, GENERIC_TEMPLATE)
            return template.format(
                position=ctx.desired_position,
                share=share,
                skill=skill.replace("_", " "),
            )
    return (
        f"Ваша готовность к роли «{ctx.desired_position}» — {ctx.readiness_score}%. "
        f"Не хватает: {', '.join(ctx.missing_skills[:3]) or '—'} . "
        f"Прогресс по плану: {ctx.plan_summary}. "
        f"Спросите про конкретный навык — расскажу, зачем он нужен."
    )