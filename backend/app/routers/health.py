"""Health check router.

Provides a simple health check endpoint for monitoring.
"""

from fastapi import APIRouter

from app.models.dto import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check endpoint")
async def health_check() -> HealthResponse:
    """Check if the API is running.

    Returns:
        HealthResponse with status 'ok'
    """
    return HealthResponse(status="ok")
