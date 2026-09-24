"""Публичный API для HR-систем и ATS."""
from __future__ import annotations

import anyio
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_employer
from app.middleware import employer_limiter
from app.models import (
    EmployerAccessLog,
    EmployerAccount,
    PlanStep,
    StudentVerification,
    User,
)
from app.schemas import (
    EmployerCandidateOut,
    EmployerRegisterRequest,
    EmployerRegisterResponse,
    EmployerSearchResponse,
)
from app.services.anonymization import anonymized_id, build_public_profile
from app.services.api_keys import generate_api_key
from app.services.skills import normalize_skill
from app.services.trudvsem import fetch_vacancies

router = APIRouter(prefix="/employer/v1", tags=["employer-api"])


@router.post("/employers/register", response_model=EmployerRegisterResponse)
def register_employer(
    payload: EmployerRegisterRequest,
    admin_secret: str = Header(..., alias="X-Admin-Secret"),
    db: Session = Depends(get_db),
) -> EmployerRegisterResponse:
    """Регистрация работодателя. В MVP защищено админ-секретом."""
    if admin_secret != settings.admin_secret:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Неверный админский секрет")

    existing = db.scalar(
        select(EmployerAccount).where(
            EmployerAccount.contact_email == payload.contact_email
        )
    )
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email уже зарегистрирован")

    raw, hashed = generate_api_key()
    employer = EmployerAccount(
        company_name=payload.company_name,
        contact_email=payload.contact_email,
        api_key_hash=hashed,
    )
    db.add(employer)
    db.commit()
    return EmployerRegisterResponse(api_key=raw, company_name=employer.company_name)


@router.get("/candidates/search", response_model=EmployerSearchResponse)
@employer_limiter.limit(settings.rate_limit_employer)
def search_candidates(
    request: Request,
    position: str = Query(..., min_length=2, max_length=200),
    skills: str = Query(default="", description="Навыки через запятую"),
    region: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
    employer: EmployerAccount = Depends(get_employer),
    db: Session = Depends(get_db),
) -> EmployerSearchResponse:
    """Поиск анонимизированных кандидатов.

    Возвращает только студентов с включённым employer_opt_in.
    """
    required_skills = {normalize_skill(s) for s in skills.split(",") if s.strip()}

    vacancies, source = anyio.run(fetch_vacancies, position, None, 50)
    vacancy_skills: set[str] = set()
    for v in vacancies:
        vacancy_skills |= v.skills
    if required_skills:
        vacancy_skills = required_skills

    query = (
        select(User)
        .where(User.desired_position.ilike(f"%{position}%"))
        .where(User.employer_opt_in.is_(True))
    )
    if region:
        query = query.where(User.region.ilike(f"%{region}%"))

    users = db.scalars(query.limit(limit * 3)).all()

    results: list[dict] = []
    for user in users:
        user_skills = {normalize_skill(s) for s in user.skills}
        matched = sorted(user_skills & vacancy_skills)
        if not matched:
            continue

        score = (
            int(round(100 * len(matched) / len(vacancy_skills)))
            if vacancy_skills
            else 0
        )

        verifications = list(
            db.scalars(
                select(StudentVerification).where(
                    StudentVerification.user_id == user.id
                )
            )
        )
        steps = list(
            db.scalars(select(PlanStep).where(PlanStep.user_id == user.id))
        )
        done = sum(1 for s in steps if s.is_done)

        profile = build_public_profile(user, verifications, score, matched)
        profile["plan_progress"] = f"{done}/{len(steps)}" if steps else "—"
        results.append(profile)

    results.sort(key=lambda p: (-p["match_score"], -p["verified_count"]))

    for r in results[:limit]:
        db.add(EmployerAccessLog(employer_id=employer.id, student_user_id=0))
    db.commit()

    return EmployerSearchResponse(
        source=source,
        total=len(results),
        items=[EmployerCandidateOut(**r) for r in results[:limit]],
    )


@router.get("/candidates/{candidate_id}", response_model=EmployerCandidateOut)
def get_candidate(
    candidate_id: str,
    employer: EmployerAccount = Depends(get_employer),
    db: Session = Depends(get_db),
) -> EmployerCandidateOut:
    """Получить профиль по candidate_id (только при opt-in)."""
    users = db.scalars(
        select(User).where(User.employer_opt_in.is_(True))
    ).all()
    target = next((u for u in users if anonymized_id(u.id) == candidate_id), None)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Кандидат не найден")

    verifications = list(
        db.scalars(
            select(StudentVerification).where(
                StudentVerification.user_id == target.id
            )
        )
    )
    steps = list(db.scalars(select(PlanStep).where(PlanStep.user_id == target.id)))
    done = sum(1 for s in steps if s.is_done)

    profile = build_public_profile(target, verifications, 0, [])
    profile["plan_progress"] = f"{done}/{len(steps)}"
    return EmployerCandidateOut(**profile)


@router.post("/candidates/{candidate_id}/request-contact")
def request_contact(
    candidate_id: str,
    employer: EmployerAccount = Depends(get_employer),
    db: Session = Depends(get_db),
) -> dict:
    """Запрос контакта. Студент получит уведомление в MAX и решит, делиться ли."""
    return {
        "status": "requested",
        "message": "Студент получит уведомление и сможет открыть контакт.",
    }