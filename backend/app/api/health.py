from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(prefix="/api",tags=["Health"])

@router.get("/health")
def health_check():

    settings = get_settings()

    return {
        "status": "healthy",
        "application": settings.app_name,
        "environment": settings.environment,
    }