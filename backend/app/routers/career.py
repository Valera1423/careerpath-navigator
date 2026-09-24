import anyio
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.middleware import limiter
from app.models import Achievement, PlanStep, User, UserProgress
from app.schemas import (
    PlanResponse,
    PlanStepOut,
    RecommendationsResponse,
    SkillGapResponse,
    VacancyOut,
)
from app.services.gamification import award_step, make_achievement
from app.services.gap import compute_gap
from app.services.plan import build_plan
from app.services.skills import normalize_skill
from app.services.trudvsem import fetch_vacancies

router = APIRouter(tags=["career"])


async def _load_vacancies_for(user: User, limit: int = 50):
    region_code = user.region if (user.region or "").isdigit() else None
    return await fetch_vacancies(
        text=user.desired_position, region_code=region_code, limit=limit
    )


@router.get("/skills/gap", response_model=SkillGapResponse)
def skill_gap(user: User = Depends(get_current_user)) -> SkillGapResponse:
    vacancies, source = anyio.run(_load_vacancies_for, user)
    return compute_gap(
        position=user.desired_position,
        region=user.region,
        user_skills=user.skills,
        vacancies=vacancies,
        source=source,
    )


def _plan_response(steps: list[PlanStep]) -> PlanResponse:
    total = len(steps)
    done = sum(1 for s in steps if s.is_done)
    return PlanResponse(
        steps=[PlanStepOut.model_validate(s) for s in steps],
        total=total,
        done=done,
        progress_percent=int(round(100 * done / total)) if total else 0,
    )


@router.get("/plan", response_model=PlanResponse)
def get_plan(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanResponse:
    steps = list(
        db.scalars(
            select(PlanStep)
            .where(PlanStep.user_id == user.id)
            .order_by(PlanStep.order_index)
        )
    )
    return _plan_response(steps)


@router.post(
    "/plan/regenerate",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.rate_limit_regenerate)
def regenerate_plan(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanResponse:
    vacancies, source = anyio.run(_load_vacancies_for, user)
    gap = compute_gap(
        position=user.desired_position,
        region=user.region,
        user_skills=user.skills,
        vacancies=vacancies,
        source=source,
    )

    db.query(PlanStep).filter(PlanStep.user_id == user.id).delete(
        synchronize_session=False
    )
    for raw in build_plan(gap.missing):
        db.add(PlanStep(user_id=user.id, **raw))
    db.commit()

    steps = list(
        db.scalars(
            select(PlanStep)
            .where(PlanStep.user_id == user.id)
            .order_by(PlanStep.order_index)
        )
    )
    return _plan_response(steps)


@router.post("/plan/steps/{step_id}/toggle", response_model=PlanStepOut)
def toggle_step(
    step_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlanStep:
    step = db.get(PlanStep, step_id)
    if not step or step.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Шаг не найден")

    step.is_done = not step.is_done

    if step.is_done:
        progress = db.scalar(
            select(UserProgress).where(UserProgress.user_id == user.id)
        )
        if not progress:
            progress = UserProgress(user_id=user.id)
            db.add(progress)
            db.flush()

        existing = {
            a.code
            for a in db.scalars(
                select(Achievement).where(Achievement.user_id == user.id)
            )
        }
        unlocked = award_step(progress, step.skill, existing)
        for code in unlocked:
            db.add(make_achievement(user.id, code))

    db.commit()
    db.refresh(step)
    return step


@router.get("/vacancies/recommendations", response_model=RecommendationsResponse)
def recommendations(
    limit: int = Query(default=8, ge=1, le=30),
    user: User = Depends(get_current_user),
) -> RecommendationsResponse:
    vacancies, source = anyio.run(_load_vacancies_for, user, 50)
    user_set = {normalize_skill(s) for s in user.skills}

    scored: list[VacancyOut] = []
    for v in vacancies:
        if not v.skills:
            continue
        matched = sorted(v.skills & user_set)
        score = int(round(100 * len(matched) / len(v.skills)))
        scored.append(
            VacancyOut(
                id=v.id,
                title=v.title,
                company=v.company,
                region=v.region,
                salary=v.salary,
                url=v.url,
                match_score=score,
                matched_skills=matched,
                published_at=v.published_at,
            )
        )

    scored.sort(key=lambda x: (-x.match_score, x.title))
    return RecommendationsResponse(source=source, items=scored[:limit])