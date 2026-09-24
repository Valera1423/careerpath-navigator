from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PlanStep, SimulatorSession, User
from app.schemas import (
    ScenarioListOut,
    SimulatorChoiceRequest,
    SimulatorChooseResponse,
    SimulatorNodeOut,
    SimulatorSessionOut,
    SkillGapItem,
)
from app.services.plan import build_plan
from app.services.simulator import apply_choice, get_node, list_scenarios, load_scenario

router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.get("/scenarios", response_model=list[ScenarioListOut])
def scenarios() -> list[dict]:
    return list_scenarios()


@router.post(
    "/sessions",
    response_model=SimulatorSessionOut,
    status_code=status.HTTP_201_CREATED,
)
def start_session(
    scenario_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    scenario = load_scenario(scenario_id)
    session = SimulatorSession(
        user_id=user.id,
        scenario_id=scenario_id,
        current_node=scenario["start_node"],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "scenario_id": session.scenario_id,
        "node": get_node(session),
    }


@router.post(
    "/sessions/{session_id}/choose",
    response_model=SimulatorChooseResponse,
)
def choose(
    session_id: int,
    payload: SimulatorChoiceRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    session = db.get(SimulatorSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сессия не найдена")
    if session.is_finished:
        raise HTTPException(status.HTTP_409_CONFLICT, "Сессия уже завершена")

    try:
        result = apply_choice(session, payload.choice_id)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    db.commit()
    return result


@router.post("/sessions/{session_id}/apply-to-profile")
def apply_to_profile(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Переносит gaps из симулятора в план развития."""
    session = db.get(SimulatorSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сессия не найдена")

    existing_gaps = set(session.gaps_found)
    if not existing_gaps:
        return {"added_skills": [], "message": "Пробелов не выявлено"}

    user_skills = set(user.skills)
    new_skills = existing_gaps - user_skills

    fake_gap = [
        SkillGapItem(skill=s, demand=1, demand_share=0.5, importance="important")
        for s in new_skills
    ]
    for raw in build_plan(fake_gap):
        db.add(PlanStep(user_id=user.id, **raw))

    db.commit()
    return {
        "added_skills": sorted(new_skills),
        "message": f"Добавлено {len(new_skills)} навыков в план",
    }