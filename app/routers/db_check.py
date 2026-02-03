"""
Database check router.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.models.request_models import DatabaseCheckRequest
from app.services.db_service import DatabaseService
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder

logger = get_logger(__name__)

router = APIRouter(prefix="/test", tags=["tests"])


@router.post("/db")
async def check_database(request: Optional[DatabaseCheckRequest] = None):
    """
    Check database connectivity and execute test query.
    
    Args:
        request: Optional request with custom database URL and query
    
    Returns:
        Database check result
    """
    logger.info("Received database check request")
    
    try:
        req = request or DatabaseCheckRequest()
        result = await DatabaseService.check_database(
            database_url=req.database_url,
            query=req.query
        )
        
        return response_builder.success(
            data=result,
            message="Database check completed"
        )
    
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_builder.error(
                error="database_check_failed",
                message=str(e),
                status_code=500
            )
        )
@router.get("/db")
async def get_database():
    """
    GET version for frontend integration (uses default config)
    """
    logger.info("Received GET database check request")
    try:
        result = await DatabaseService.check_database()
        return response_builder.success(
            data=result,
            message="Database check completed"
        )
    except Exception as e:
        logger.error(f"Database GET check failed: {e}")
        return response_builder.error(error="db_check_failed", message=str(e), status_code=500)
