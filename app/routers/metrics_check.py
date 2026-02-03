"""
Metrics check router.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.models.request_models import MetricsCheckRequest
from app.services.metrics_service import MetricsService
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder

logger = get_logger(__name__)

router = APIRouter(prefix="/test", tags=["tests"])


@router.post("/metrics")
async def check_metrics(request: Optional[MetricsCheckRequest] = None):
    """
    Check Azure VM metrics (CPU and Memory).
    
    Args:
        request: Optional request with custom resource ID and thresholds
    
    Returns:
        Metrics check results
    """
    logger.info("Received metrics check request")
    
    try:
        req = request or MetricsCheckRequest()
        result = await MetricsService.check_metrics(
            resource_id=req.resource_id,
            cpu_threshold=req.cpu_threshold,
            memory_threshold=req.memory_threshold
        )
        
        return response_builder.success(
            data=result,
            message="Metrics check completed"
        )
    
    except Exception as e:
        logger.error(f"Metrics check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_builder.error(
                error="metrics_check_failed",
                message=str(e),
                status_code=500
            )
        )
@router.get("/metrics")
async def get_metrics():
    """
    GET version for frontend integration (uses default config)
    """
    logger.info("Received GET metrics check request")
    try:
        result = await MetricsService.check_metrics()
        return response_builder.success(
            data=result,
            message="Metrics check completed"
        )
    except Exception as e:
        logger.error(f"Metrics GET check failed: {e}")
        return response_builder.error(error="metrics_check_failed", message=str(e), status_code=500)
