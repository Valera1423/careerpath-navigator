from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import InterviewSession, User
from app.schemas import (
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    InterviewQuestionOut,
    InterviewSessionOut,
)
from app.services.interview import evaluate_answer, questions_for

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/sessions", response_model=InterviewQuestionOut, status_code=status.HTTP_201_CREATED)
def start_session(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewQuestionOut:
    questions = questions_for(user.desired_position, limit=5)
    session = InterviewSession(
        user_id=user.id,
        position=user.desired_position,
        questions=questions,
        answers=[],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return InterviewQuestionOut(
        session_id=session.id,
        question_index=0,
        total=len(questions),
        question=questions[0],
    )


@router.post("/sessions/{session_id}/answer", response_model=InterviewAnswerResponse)
def submit_answer(
    session_id: int,
    payload: InterviewAnswerRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewAnswerResponse:
    session = db.get(InterviewSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сессия не найдена")
    if session.is_finished:
        raise HTTPException(status.HTTP_409_CONFLICT, "Сессия завершена")

    star = evaluate_answer(payload.answer)
    idx = len(session.answers)
    session.answers = [
        *session.answers,
        {
            "question": session.questions[idx],
            "answer": payload.answer,
            "score": star.score,
            "feedback": star.feedback,
        },
    ]
    session.total_score += star.score

    is_finished = len(session.answers) >= len(session.questions)
    session.is_finished = is_finished
    db.commit()

    next_q = None if is_finished else session.questions[len(session.answers)]

    return InterviewAnswerResponse(
        score=star.score,
        feedback=star.feedback,
        structure={
            "situation": star.situation,
            "task": star.task,
            "action": star.action,
            "result": star.result,
        },
        next_question=next_q,
        is_finished=is_finished,
    )


@router.get("/sessions/{session_id}", response_model=InterviewSessionOut)
def get_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewSessionOut:
    session = db.get(InterviewSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сессия не найдена")
    return InterviewSessionOut(
        session_id=session.id,
        position=session.position,
        total=len(session.questions),
        answered=len(session.answers),
        total_score=session.total_score,
        is_finished=session.is_finished,
    )