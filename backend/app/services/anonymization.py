"""Анонимизация профиля студента для выдачи работодателям.

PII (имя, email, точный ID) никогда не покидают БД.
Регион округляется до федерального округа.
"""
from __future__ import annotations

import hashlib

from app.models import StudentVerification, User

REGION_TO_OKRUG = {
    "москва": "ЦФО",
    "московская": "ЦФО",
    "тульская": "ЦФО",
    "тверская": "ЦФО",
    "санкт-петербург": "СЗФО",
    "ленинградская": "СЗФО",
    "новгородская": "СЗФО",
    "казань": "ПФО",
    "татарстан": "ПФО",
    "самара": "ПФО",
    "нижний новгород": "ПФО",
    "екатеринбург": "УФО",
    "свердловская": "УФО",
    "челябинская": "УФО",
    "новосибирск": "СФО",
    "красноярск": "СФО",
    "омск": "СФО",
    "томск": "СФО",
    "краснодар": "ЮФО",
    "ростов": "ЮФО",
    "сочи": "ЮФО",
    "волгоград": "ЮФО",
    "владивосток": "ДФО",
    "хабаровск": "ДФО",
    "якутск": "ДФО",
}


def anonymize_region(region: str | None) -> str | None:
    if not region:
        return None
    lower = region.lower()
    for key, okrug in REGION_TO_OKRUG.items():
        if key in lower:
            return okrug
    return "Другой"


def anonymized_id(user_id: int) -> str:
    """Стабильный, но необратимый идентификатор для API."""
    return hashlib.sha256(f"careerpath:{user_id}".encode()).hexdigest()[:16]


def build_public_profile(
    user: User,
    verifications: list[StudentVerification],
    match_score: int,
    matched_skills: list[str],
) -> dict:
    """Формирует анонимизированный профиль для выдачи через API."""
    verified_skills = {v.skill for v in verifications}

    return {
        "candidate_id": anonymized_id(user.id),
        "region": anonymize_region(user.region),
        "experience": user.experience,
        "desired_position": user.desired_position,
        "match_score": match_score,
        "matched_skills": matched_skills,
        "skills": [
            {
                "name": s,
                "verified": s in verified_skills,
                "evidence": next(
                    (v.evidence_type for v in verifications if v.skill == s), None
                ),
            }
            for s in user.skills
        ],
        "plan_progress": None,
        "verified_count": len(verified_skills),
        "total_skills": len(user.skills),
    }