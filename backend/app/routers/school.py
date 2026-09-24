from fastapi import APIRouter, Query

from app.schemas import (
    DayInLifeResponse,
    SchoolQuestionOut,
    SchoolTestRequest,
    SchoolTestResponse,
)
from app.services.career_test import day_in_life, evaluate, list_questions

router = APIRouter(prefix="/school", tags=["school"])


@router.get("/questions", response_model=list[SchoolQuestionOut])
def questions() -> list[dict]:
    return list_questions()


@router.post("/evaluate", response_model=SchoolTestResponse)
def run_test(payload: SchoolTestRequest) -> SchoolTestResponse:
    result = evaluate(payload.answers)
    return SchoolTestResponse(
        scores=result.scores,
        top_type=result.top_type,
        professions=result.professions,
        description=result.description,
    )


@router.get("/day-in-life", response_model=DayInLifeResponse)
def day(profession: str = Query(..., min_length=2)) -> DayInLifeResponse:
    timeline = day_in_life(profession) or []
    return DayInLifeResponse(profession=profession, timeline=timeline)