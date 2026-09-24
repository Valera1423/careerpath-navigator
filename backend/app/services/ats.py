"""ATS-анализ: сравнение резюме с требованиями вакансии.

Скоринг:
- 40% — keyword matching (совпадение навыков)
- 30% — форматирование (штраф за «нечитаемые» элементы)
- 30% — наличие обязательных секций
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.skills import extract_skills, normalize_skill

BAD_FORMAT_PATTERNS = [
    (r"\t{3,}", "Множественные табуляции — ATS может склеить колонки"),
    (r"[│┃┆┇┊┋]", "Псевдографика в тексте — парсер её не прочитает"),
    (r"(?i)(фото|photo|аватар)", "Фото в резюме — ATS игнорирует изображения"),
    (r"<[^>]+>", "HTML-теги в тексте — парсер может их не распознать"),
    (r"\s{4,}", "Длинные последовательности пробелов — вероятна вёрстка таблицей"),
]

REQUIRED_SECTIONS = ["опыт", "навык", "образован", "контакт"]


@dataclass
class AtsResult:
    score: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    format_issues: list[str]
    section_warnings: list[str]


def analyze(resume_text: str, vacancy_text: str, vacancy_skills: set[str]) -> AtsResult:
    resume_norm = normalize_skill(resume_text)
    resume_skills = extract_skills(resume_text)

    # 1. Keyword matching (40%)
    matched = sorted(resume_skills & vacancy_skills)
    missing = sorted(vacancy_skills - resume_skills)
    kw_score = (len(matched) / len(vacancy_skills) * 40) if vacancy_skills else 40

    # 2. Format scoring (30%)
    format_issues: list[str] = []
    for pattern, msg in BAD_FORMAT_PATTERNS:
        if re.search(pattern, resume_text):
            format_issues.append(msg)
    fmt_score = max(0, 30 - len(format_issues) * 10)

    # 3. Section presence (30%)
    section_warnings: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in resume_norm:
            section_warnings.append(f"Не найдена секция «{section}»")
    sec_score = max(0, 30 - len(section_warnings) * 8)

    return AtsResult(
        score=int(round(kw_score + fmt_score + sec_score)),
        matched_keywords=matched,
        missing_keywords=missing,
        format_issues=format_issues,
        section_warnings=section_warnings,
    )