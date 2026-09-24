from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import ResumeUploadResponse
from app.services.resume import extract_skills_from_resume

router = APIRouter(prefix="/users/me", tags=["resume"])


@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeUploadResponse:
    content = await file.read()
    try:
        detected = extract_skills_from_resume(file.filename or "resume", content)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    existing = set(user.skills)
    added = sorted(set(detected) - existing)
    user.skills = sorted(existing | set(detected))
    db.commit()
    db.refresh(user)
    return ResumeUploadResponse(added_skills=added, total_skills=user.skills)