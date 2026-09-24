from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import EmployerAccount, User
from app.services.api_keys import verify_api_key
from app.services.max_auth import verify_init_data


def get_current_user(
    authorization: str | None = Header(default=None),
    x_max_init_data: str | None = Header(default=None, alias="X-Max-Init-Data"),
    x_max_user_id: str | None = Header(default=None, alias="X-Max-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    raw: str | None = None
    if authorization and authorization.startswith("MaxInit "):
        raw = authorization.removeprefix("MaxInit ").strip()
    elif x_max_init_data:
        raw = x_max_init_data

    if raw is not None:
        max_user = verify_init_data(raw)
        user_id = max_user.id
    elif settings.allow_insecure_init_data and x_max_user_id:
        user_id = x_max_user_id
    else:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Требуется initData от MAX Bridge",
        )

    user = db.scalar(select(User).where(User.max_user_id == user_id))
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Профиль не найден. Пройдите онбординг.",
        )
    return user


def get_employer(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> EmployerAccount:
    if not x_api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Заголовок X-API-Key обязателен")

    employers = db.scalars(
        select(EmployerAccount).where(EmployerAccount.is_active)
    ).all()
    for employer in employers:
        if verify_api_key(x_api_key, employer.api_key_hash):
            return employer

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный API-ключ")