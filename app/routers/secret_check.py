"""
Secret check router.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.models.request_models import SecretCheckRequest
from app.services.secret_service import SecretService
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder

logger = get_logger(__name__)

router = APIRouter(prefix="/test", tags=["tests"])


@router.post("/secrets")
async def check_secrets(request: Optional[SecretCheckRequest] = None):
    """
    Check Azure KeyVault secrets.
    
    Args:
        request: Optional request with custom KeyVault name and secret list
    
    Returns:
        Secret check results
    """
    logger.info("Received secret check request")
    
    try:
        req = request or SecretCheckRequest()
        result = await SecretService.check_secrets(
            keyvault_name=req.keyvault_name,
            secret_list=req.secret_list
        )
        
        return response_builder.success(
            data=result,
            message="Secret check completed"
        )
    
    except Exception as e:
        logger.error(f"Secret check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_builder.error(
                error="secret_check_failed",
                message=str(e),
                status_code=500
            )
        )
@router.get("/secrets")
async def get_secrets():
    """
    GET version for frontend integration (uses default config)
    """
    logger.info("Received GET secrets check request")
    try:
        result = await SecretService.check_secrets()
        return response_builder.success(
            data=result,
            message="Secret check completed"
        )
    except Exception as e:
        logger.error(f"Secrets GET check failed: {e}")
        return response_builder.error(error="secrets_check_failed", message=str(e), status_code=500)
