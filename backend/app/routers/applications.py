from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Application, User
from app.schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Application]:
    return list(
        db.scalars(
            select(Application)
            .where(Application.user_id == user.id)
            .order_by(Application.applied_at.desc())
        )
    )


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Application:
    remind_at = None
    if payload.remind_in_days:
        remind_at = datetime.now(timezone.utc) + timedelta(days=payload.remind_in_days)

    app = Application(
        user_id=user.id,
        vacancy_id=payload.vacancy_id,
        vacancy_title=payload.vacancy_title,
        vacancy_url=payload.vacancy_url,
        company=payload.company,
        note=payload.note,
        remind_at=remind_at,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.patch("/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Application:
    app = db.get(Application, app_id)
    if not app or app.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Отклик не найден")

    if payload.status is not None:
        app.status = payload.status
    if payload.note is not None:
        app.note = payload.note
    if payload.remind_in_days is not None:
        app.remind_at = datetime.now(timezone.utc) + timedelta(days=payload.remind_in_days)

    db.commit()
    db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    app_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    app = db.get(Application, app_id)
    if not app or app.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Отклик не найден")
    db.delete(app)
    db.commit()