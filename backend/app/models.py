from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    max_user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    desired_position: Mapped[str] = mapped_column(String(200), index=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    experience: Mapped[str] = mapped_column(String(50), default="none")
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    # 152-ФЗ: согласие на обработку ПДн
    consent_pd_given_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    employer_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    employer_opt_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 152-ФЗ ст. 9 ч. 6: обработка ПДн несовершеннолетних только
    # с согласия законного представителя.
    is_minor: Mapped[bool] = mapped_column(Boolean, default=False)
    age_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consent_pd_guardian_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    steps: Mapped[list["PlanStep"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="PlanStep.order_index",
    )


class PlanStep(Base):
    __tablename__ = "plan_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    skill: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    kind: Mapped[str] = mapped_column(String(30), default="course")
    resource_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    depends_on: Mapped[list[int]] = mapped_column(JSON, default=list)

    user: Mapped[User] = relationship(back_populates="steps")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[str] = mapped_column(String(30), default="intern")
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(60), index=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    vacancy_id: Mapped[str] = mapped_column(String(120))
    vacancy_title: Mapped[str] = mapped_column(String(300))
    vacancy_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="applied")
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    remind_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[str] = mapped_column(String(200))
    questions: Mapped[list[str]] = mapped_column(JSON, default=list)
    answers: Mapped[list[dict]] = mapped_column(JSON, default=list)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class EmployerAccount(Base):
    __tablename__ = "employer_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(200), index=True)
    contact_email: Mapped[str] = mapped_column(String(200), unique=True)
    api_key_hash: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit_per_hour: Mapped[int] = mapped_column(Integer, default=1000)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class StudentVerification(Base):
    __tablename__ = "student_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    skill: Mapped[str] = mapped_column(String(80))
    evidence_type: Mapped[str] = mapped_column(String(40))
    evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    verified_by: Mapped[str] = mapped_column(String(40), default="auto")


class EmployerAccessLog(Base):
    __tablename__ = "employer_access_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employer_id: Mapped[int] = mapped_column(
        ForeignKey("employer_accounts.id"), index=True
    )
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class SimulatorSession(Base):
    __tablename__ = "simulator_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    scenario_id: Mapped[str] = mapped_column(String(80))
    current_node: Mapped[str] = mapped_column(String(80))
    path_taken: Mapped[list[str]] = mapped_column(JSON, default=list)
    skills_gained: Mapped[list[str]] = mapped_column(JSON, default=list)
    gaps_found: Mapped[list[str]] = mapped_column(JSON, default=list)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class VacancyCache(Base):
    __tablename__ = "vacancy_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(300), unique=True, index=True)
    payload: Mapped[list[dict]] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, index=True
    )


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    event_name: Mapped[str] = mapped_column(String(60), index=True)
    properties: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, index=True
    )