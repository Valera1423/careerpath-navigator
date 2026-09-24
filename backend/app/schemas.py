from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Users ----------

class OnboardingRequest(BaseModel):
    max_user_id: str = Field(min_length=1, max_length=64)
    full_name: str | None = Field(default=None, max_length=200)
    desired_position: str = Field(min_length=2, max_length=200)
    region: str | None = Field(default=None, max_length=120)
    experience: Literal["none", "internship", "junior"] = "none"
    skills: list[str] = Field(default_factory=list, max_length=60)
    consent_pd: bool = Field(..., description="Согласие на обработку ПДн (152-ФЗ)")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    max_user_id: str
    full_name: str | None
    desired_position: str
    region: str | None
    experience: str
    skills: list[str]
    created_at: datetime
    consent_pd_given_at: datetime | None
    employer_opt_in: bool
    # 152-ФЗ ст.9 ч.6 — несовершеннолетние
    is_minor: bool = False
    age_confirmed_at: datetime | None = None
    consent_pd_guardian_at: datetime | None = None


class AgeConfirmation(BaseModel):
    """Подтверждение возраста при входе в школьный раздел."""
    birth_year: int = Field(ge=1900, le=2100)
    is_minor_declared: bool = Field(
        ...,
        description="Пользователь подтверждает, что ему меньше 18 лет",
    )


class GuardianConsent(BaseModel):
    """Согласие законного представителя (родителя/опекуна)."""
    guardian_name: str = Field(min_length=2, max_length=200)
    consent_pd_guardian: bool = Field(
        ...,
        description="Законный представитель даёт согласие на обработку ПДн",
    )


class SkillsUpdate(BaseModel):
    skills: list[str] = Field(default_factory=list, max_length=60)


class OptInRequest(BaseModel):
    employer_opt_in: bool


# ---------- Gap / Plan ----------

class SkillGapItem(BaseModel):
    skill: str
    demand: int
    demand_share: float
    importance: Literal["critical", "important", "nice-to-have"]


class SkillGapResponse(BaseModel):
    position: str
    region: str | None
    vacancies_analyzed: int
    source: Literal["trudvsem", "fallback"]
    matched: list[SkillGapItem]
    missing: list[SkillGapItem]
    readiness_score: int


class PlanStepOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_index: int
    skill: str
    title: str
    description: str
    kind: str
    resource_url: str | None
    is_done: bool
    due_date: datetime | None = None
    depends_on: list[int] = Field(default_factory=list)


class PlanResponse(BaseModel):
    steps: list[PlanStepOut]
    total: int
    done: int
    progress_percent: int


# ---------- Vacancies ----------

class VacancyOut(BaseModel):
    id: str
    title: str
    company: str
    region: str
    salary: str | None
    url: str | None
    match_score: int
    matched_skills: list[str]
    published_at: str | None


class RecommendationsResponse(BaseModel):
    source: Literal["trudvsem", "fallback"]
    items: list[VacancyOut]


# ---------- Resume / ATS ----------

class ResumeUploadResponse(BaseModel):
    added_skills: list[str]
    total_skills: list[str]


class AtsAnalyzeResponse(BaseModel):
    score: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    format_issues: list[str]
    section_warnings: list[str]


# ---------- Portfolio ----------

class PortfolioReadmeRequest(BaseModel):
    project_name: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    skills: list[str] = Field(default_factory=list)


class PortfolioReadmeResponse(BaseModel):
    readme: str


class PortfolioBulletRequest(BaseModel):
    project_name: str = Field(min_length=2, max_length=200)
    skills: list[str]
    outcome: str | None = None


class PortfolioBulletResponse(BaseModel):
    bullet: str


# ---------- Market ----------

class MarketTrendsResponse(BaseModel):
    period_days: int
    vacancies_analyzed: int
    top_skills: list[dict]
    top_companies: list[dict]
    salaries: dict


class ForecastItem(BaseModel):
    skill: str
    current: int
    predicted: int
    trend: str
    change_pct: int


class ForecastResponse(BaseModel):
    horizon_months: int
    items: list[ForecastItem]


# ---------- Coach ----------

class CoachAskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class CoachAskResponse(BaseModel):
    answer: str
    used_llm: bool


# ---------- Gamification ----------

class ProgressOut(BaseModel):
    xp: int
    level: str
    level_label: str
    current_threshold: int
    next_threshold: int
    streak_days: int


class AchievementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    title: str
    description: str
    unlocked_at: datetime


# ---------- Compass ----------

class CompassGraphResponse(BaseModel):
    nodes: list[dict]
    edges: list[dict]


# ---------- Interview ----------

class InterviewQuestionOut(BaseModel):
    session_id: int
    question_index: int
    total: int
    question: str


class InterviewAnswerRequest(BaseModel):
    answer: str = Field(min_length=5, max_length=4000)


class InterviewAnswerResponse(BaseModel):
    score: int
    feedback: str
    structure: dict
    next_question: str | None
    is_finished: bool


class InterviewSessionOut(BaseModel):
    session_id: int
    position: str
    total: int
    answered: int
    total_score: int
    is_finished: bool


# ---------- School ----------

class SchoolQuestionOut(BaseModel):
    id: int
    text: str
    type: str


class SchoolTestRequest(BaseModel):
    answers: dict[int, int]


class SchoolTestResponse(BaseModel):
    scores: dict[str, int]
    top_type: str
    professions: list[str]
    description: str


class DayInLifeResponse(BaseModel):
    profession: str
    timeline: list[str]


# ---------- Applications ----------

class ApplicationCreate(BaseModel):
    vacancy_id: str = Field(min_length=1, max_length=120)
    vacancy_title: str = Field(min_length=1, max_length=300)
    vacancy_url: str | None = Field(default=None, max_length=500)
    company: str | None = Field(default=None, max_length=200)
    note: str | None = None
    remind_in_days: int | None = Field(default=None, ge=1, le=90)


class ApplicationUpdate(BaseModel):
    status: Literal["applied", "interview", "offer", "rejected"] | None = None
    note: str | None = None
    remind_in_days: int | None = Field(default=None, ge=1, le=90)


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vacancy_id: str
    vacancy_title: str
    vacancy_url: str | None
    company: str | None
    status: str
    applied_at: datetime
    remind_at: datetime | None
    note: str | None


# ---------- Leaderboard ----------

class LeaderboardEntry(BaseModel):
    rank: int
    display_name: str
    xp: int
    level: str
    streak_days: int


# ---------- Employer API ----------

class EmployerRegisterRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=200)
    contact_email: str = Field(min_length=5, max_length=200)


class EmployerRegisterResponse(BaseModel):
    api_key: str
    company_name: str


class EmployerCandidateOut(BaseModel):
    candidate_id: str
    region: str | None
    experience: str
    desired_position: str
    match_score: int
    matched_skills: list[str]
    skills: list[dict]
    plan_progress: str | None
    verified_count: int
    total_skills: int


class EmployerSearchResponse(BaseModel):
    source: str
    total: int
    items: list[EmployerCandidateOut]


# ---------- Simulator ----------

class ScenarioListOut(BaseModel):
    id: str
    role: str
    duration_minutes: int
    intro: str


class SimulatorChoiceRequest(BaseModel):
    choice_id: str


class SimulatorNodeOut(BaseModel):
    node_id: str
    type: str
    text: str
    choices: list[dict]
    outcome: str | None = None
    summary: str | None = None


class SimulatorChooseResponse(BaseModel):
    feedback: str = ""
    effects: dict[str, Any] = Field(default_factory=dict)
    next: SimulatorNodeOut
    is_finished: bool


class SimulatorSessionOut(BaseModel):
    session_id: int
    scenario_id: str
    node: dict


# ---------- Admin / Analytics ----------

class AnalyticsEventIn(BaseModel):
    event_name: str = Field(min_length=2, max_length=60)
    user_id: int | None = None
    properties: dict[str, Any] = Field(default_factory=dict)