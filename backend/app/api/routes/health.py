"""Health check endpoints."""

from fastapi import APIRouter
import logging

from app.api.models.responses import HealthResponse
from app.core.dataset import get_dataset_manager
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        Service status and dataset load status
    """
    try:
        dataset_manager = get_dataset_manager()
        dataset_loaded = dataset_manager.is_loaded()

        return HealthResponse(
            status="healthy" if dataset_loaded else "degraded",
            dataset_loaded=dataset_loaded,
            version=settings.app_version,
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            dataset_loaded=False,
            version=settings.app_version,
        )
