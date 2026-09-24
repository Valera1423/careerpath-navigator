from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}