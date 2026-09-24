"""Подключение к БД, сессии, базовый класс для моделей."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Общий Declarative Base для всех моделей."""
    pass


def _build_engine():
    url = settings.database_url
    kwargs: dict = {"future": True}

    if url.startswith("sqlite"):
        # SQLite + многопоточный FastAPI — обязательно check_same_thread=False
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_pre_ping"] = True

    return create_engine(url, **kwargs)


engine = _build_engine()
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI-зависимость: одна сессия на запрос."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Создать таблицы (fallback для локальной разработки без alembic)."""
    from app import models  # noqa: F401  — регистрирует модели в Base.metadata

    Base.metadata.create_all(bind=engine)