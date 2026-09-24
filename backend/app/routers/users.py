from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.middleware import limiter
from app.models import User
from app.schemas import (
    AgeConfirmation,
    GuardianConsent,
    OnboardingRequest,
    SkillsUpdate,
    UserOut,
)

router = APIRouter(prefix="/users", tags=["users"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


@router.post("/onboarding", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_onboarding)
def onboarding(
    request: Request,
    payload: OnboardingRequest,
    db: Session = Depends(get_db),
) -> User:
    user = db.scalar(select(User).where(User.max_user_id == payload.max_user_id))
    if user is None:
        user = User(max_user_id=payload.max_user_id)
        db.add(user)

    user.full_name = payload.full_name
    user.desired_position = payload.desired_position
    user.region = payload.region
    user.experience = payload.experience
    user.skills = sorted({s.strip().lower() for s in payload.skills if s.strip()})

    # 152-ФЗ: фиксируем момент согласия (только если оно дано)
    if payload.consent_pd and user.consent_pd_given_at is None:
        user.consent_pd_given_at = _now()

    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me/skills", response_model=UserOut)
def update_skills(
    payload: SkillsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    user.skills = sorted({s.strip().lower() for s in payload.skills if s.strip()})
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/employer-opt-in", response_model=UserOut)
def set_employer_opt_in(
    payload: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Включение/выключение передачи данных работодателям.

    Отдельно от онбординга: пользователь может передумать в любой момент.
    """
    enabled = bool(payload.get("employer_opt_in"))
    user.employer_opt_in = enabled
    user.employer_opt_in_at = _now() if enabled else None
    db.commit()
    db.refresh(user)
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Удаление профиля и всех связанных данных (152-ФЗ ст. 21).

    Каскадное удаление: шаги плана, отклики, интервью, симуляторы,
    достижения, прогресс — всё связано через FK ON DELETE CASCADE.
    """
    db.delete(user)
    db.commit()


# ---------- 152-ФЗ ст.9 ч.6: несовершеннолетние ----------


@router.post("/me/age-confirmation", response_model=UserOut)
def confirm_age(
    payload: AgeConfirmation,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Пользователь подтверждает возраст при входе в раздел «Школьникам».

    Если ему меньше 18, требуется согласие законного представителя —
    без него школьный раздел закрыт.
    """
    current_year = _now().year
    calculated_age = current_year - payload.birth_year

    if calculated_age < 0 or calculated_age > 120:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Некорректный год рождения",
        )

    is_minor = calculated_age < 18
    user.is_minor = is_minor
    user.age_confirmed_at = _now()

    db.commit()
    db.refresh(user)
    return user


@router.post("/me/guardian-consent", response_model=UserOut)
def set_guardian_consent(
    payload: GuardianConsent,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Согласие законного представителя на обработку ПДн несовершеннолетнего.

    По 152-ФЗ ст. 9 ч. 6 обработка ПДн несовершеннолетнего допускается
    только с согласия родителя/опекуна. Без этого поля школьный раздел
    недоступен.
    """
    if not user.age_confirmed_at:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Сначала подтвердите возраст",
        )
    if not user.is_minor:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Согласие законного представителя требуется только для лиц младше 18 лет",
        )
    if not payload.consent_pd_guardian:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Без согласия законного представителя доступ к разделу закрыт",
        )

    user.consent_pd_guardian_at = _now()
    db.commit()
    db.refresh(user)
    return user