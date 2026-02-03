"""
API check router.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.models.request_models import ApiCheckRequest
from app.services.api_service import ApiService
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder

logger = get_logger(__name__)

router = APIRouter(prefix="/test", tags=["tests"])


@router.post("/apis")
async def check_apis(request: Optional[ApiCheckRequest] = None):
    """
    Check multiple application APIs.
    
    Args:
        request: Optional request with custom API list
    
    Returns:
        API check results
    """
    logger.info("Received API check request")
    
    try:
        req = request or ApiCheckRequest()
        result = await ApiService.check_apis(
            api_list=req.api_list
        )
        
        return response_builder.success(
            data=result,
            message="API check completed"
        )
    
    except Exception as e:
        logger.error(f"API check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_builder.error(
                error="api_check_failed",
                message=str(e),
                status_code=500
            )
        )
@router.get("/apis")
async def get_apis():
    """
    GET version for frontend integration (uses default config)
    """
    logger.info("Received GET API check request")
    try:
        result = await ApiService.check_apis()
        return response_builder.success(
            data=result,
            message="API check completed"
        )
    except Exception as e:
        logger.error(f"API GET check failed: {e}")
        return response_builder.error(error="api_check_failed", message=str(e), status_code=500)
