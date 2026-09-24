"""Генерация README и bullet-point для резюме."""
from __future__ import annotations

FENCE = "`" * 3

README_TEMPLATE = (
    "# {project_name}\n\n"
    "## Описание\n"
    "{description}\n\n"
    "## Стек\n"
    "{stack}\n\n"
    "## Что сделано\n"
    "- [ ] Основной функционал\n"
    "- [ ] Тесты (pytest / vitest)\n"
    "- [ ] CI (GitHub Actions)\n"
    "- [ ] README с инструкцией запуска\n"
    "- [ ] Деплой (если применимо)\n\n"
    "## Как запустить\n"
    + FENCE + "bash\n"
    "{run_commands}\n"
    + FENCE + "\n\n"
    "## Скриншоты\n"
    "<!-- Добавьте 1–2 скриншота работы приложения -->\n\n"
    "## Контакты\n"
    "Автор: {author}\n"
)

DEFAULT_RUN_COMMANDS = (
    "# TODO: опишите команды запуска\n"
    "# Например:\n"
    "# docker compose up --build\n"
    "# или\n"
    "# pip install -r requirements.txt && uvicorn app.main:app --reload"
)


def generate_readme(
    project_name: str,
    description: str,
    skills: list[str],
    author: str,
    run_commands: str | None = None,
) -> str:
    cleaned = _clean_skills(skills)
    stack = ", ".join(cleaned) if cleaned else "—"
    return README_TEMPLATE.format(
        project_name=project_name.strip(),
        description=description.strip(),
        stack=stack,
        run_commands=(run_commands or DEFAULT_RUN_COMMANDS).strip(),
        author=author.strip() or "Автор",
    )


def generate_resume_bullet(
    project_name: str,
    skills: list[str],
    outcome: str | None = None,
) -> str:
    cleaned = _clean_skills(skills)
    stack = ", ".join(cleaned[:4]) if cleaned else "современных технологий"
    base = f"Разработал «{project_name.strip()}» с использованием {stack}"
    if outcome and outcome.strip():
        base += f". Результат: {outcome.strip()}"
    return base + "."


def _clean_skills(skills: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in skills:
        s = (raw or "").strip().lower()
        if not s or s in seen:
            continue
        seen.add(s)
        result.append(s)
    return result