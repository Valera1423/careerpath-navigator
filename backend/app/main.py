import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.middleware import limiter
from app.routers import (
    applications,
    ats,
    career,
    coach,
    compass,
    employer_api,
    export,
    gamification,
    health,
    interview,
    leaderboard,
    market,
    market_forecast,
    portfolio,
    resume,
    school,
    simulator,
    users,
    webhook,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # В прод-режиме схема обновляется через alembic upgrade head в entrypoint.
    # init_db() только для локальной разработки без alembic.
    if settings.database_url.startswith("sqlite"):
        init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="CareerPath Navigator — карьерное сопровождение для MAX.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)

app.include_router(health.router)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(career.router, prefix=settings.api_prefix)
app.include_router(resume.router, prefix=settings.api_prefix)
app.include_router(ats.router, prefix=settings.api_prefix)
app.include_router(portfolio.router, prefix=settings.api_prefix)
app.include_router(market.router, prefix=settings.api_prefix)
app.include_router(market_forecast.router, prefix=settings.api_prefix)
app.include_router(coach.router, prefix=settings.api_prefix)
app.include_router(gamification.router, prefix=settings.api_prefix)
app.include_router(compass.router, prefix=settings.api_prefix)
app.include_router(interview.router, prefix=settings.api_prefix)
app.include_router(school.router, prefix=settings.api_prefix)
app.include_router(applications.router, prefix=settings.api_prefix)
app.include_router(leaderboard.router, prefix=settings.api_prefix)
app.include_router(employer_api.router, prefix=settings.api_prefix)
app.include_router(simulator.router, prefix=settings.api_prefix)
app.include_router(export.router, prefix=settings.api_prefix)
app.include_router(webhook.router)