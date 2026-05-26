from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["System"])

@router.get("/health", status_code=200)
async def health_check():
    """
    Standard kubernetes-friendly health check endpoint.
    Used by readiness and liveness probes.
    """
    return {
        "service": "api-gateway",
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }
