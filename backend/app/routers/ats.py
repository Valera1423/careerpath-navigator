from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.dependencies import get_current_user
from app.models import User
from app.schemas import AtsAnalyzeResponse
from app.services.ats import analyze
from app.services.resume import extract_text
from app.services.skills import extract_skills

router = APIRouter(prefix="/ats", tags=["ats"])


@router.post("/analyze", response_model=AtsAnalyzeResponse)
async def ats_analyze(
    file: UploadFile = File(...),
    vacancy_text: str = Form(default=""),
    user: User = Depends(get_current_user),
) -> AtsAnalyzeResponse:
    content = await file.read()
    try:
        resume_text = extract_text(file.filename or "resume", content)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    if not vacancy_text.strip():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Вставьте текст вакансии"
        )

    vacancy_skills = extract_skills(vacancy_text)
    result = analyze(resume_text, vacancy_text, vacancy_skills)
    return AtsAnalyzeResponse(**result.__dict__)