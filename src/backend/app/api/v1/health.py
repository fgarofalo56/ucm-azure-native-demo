"""Health and readiness probe endpoints."""

import structlog
from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.db.session import async_session_factory
from app.dependencies import get_blob_service_client
from app.models.schemas import HealthResponse, ReadinessResponse

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check - always returns 200 if the app is running."""
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        version="0.1.0",
    )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    """Readiness probe - checks database and storage connectivity."""
    checks: dict[str, bool] = {}

    # Check database
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.warning("readiness_check_db_failed", error=str(e))
        checks["database"] = False

    # Check blob storage
    try:
        client = get_blob_service_client()
        container = client.get_container_client(settings.azure_storage_container_name)
        container.get_container_properties()
        checks["storage"] = True
    except Exception as e:
        logger.warning("readiness_check_storage_failed", error=str(e))
        checks["storage"] = False

    all_healthy = all(checks.values())
    return ReadinessResponse(
        status="ready" if all_healthy else "not_ready",
        checks=checks,
    )
