"""
Run all tests router.
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status

from app.models.request_models import RunAllRequest
from app.services.db_service import DatabaseService
from app.services.api_service import ApiService
from app.services.secret_service import SecretService
from app.services.metrics_service import MetricsService
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder

logger = get_logger(__name__)

router = APIRouter(tags=["tests"])


@router.post("/run-all")
async def run_all_tests(request: Optional[RunAllRequest] = None):
    """
    Run all available smoke tests.
    
    Args:
        request: Optional request with test configurations
    
    Returns:
        Summary and details of all test results
    """
    req = request or RunAllRequest()
    run_id = str(uuid.uuid4())
    
    logger.info(f"Starting run-all tests with run_id: {run_id}")
    
    try:
        results = {}
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "warning_tests": 0,
            "failed_tests": 0
        }
        
        # Run database check
        if req.include_db_check:
            logger.info("Running database check")
            db_req = req.db_request or {}
            db_result = await DatabaseService.check_database(
                database_url=db_req.get("database_url") if isinstance(db_req, dict) else db_req.database_url,
                query=db_req.get("query") if isinstance(db_req, dict) else db_req.query
            )
            results["database"] = db_result
            summary["total_tests"] += 1
            if db_result["status"] == "UP":
                summary["passed_tests"] += 1
            elif "ERROR" in db_result["status"] or "DOWN" in db_result["status"]:
                summary["failed_tests"] += 1
            else:
                summary["warning_tests"] += 1
        
        # Run API check
        if req.include_api_check:
            logger.info("Running API check")
            api_req = req.api_request or {}
            api_result = await ApiService.check_apis(
                api_list=api_req.get("api_list") if isinstance(api_req, dict) else api_req.api_list
            )
            results["apis"] = api_result
            summary["total_tests"] += 1
            if api_result["status"] == "OK":
                summary["passed_tests"] += 1
            elif api_result["status"] == "WARNING":
                summary["warning_tests"] += 1
            else:
                summary["failed_tests"] += 1
        
        # Run secret check
        if req.include_secret_check:
            logger.info("Running secret check")
            secret_req = req.secret_request or {}
            secret_result = await SecretService.check_secrets(
                keyvault_name=secret_req.get("keyvault_name") if isinstance(secret_req, dict) else secret_req.keyvault_name,
                secret_list=secret_req.get("secret_list") if isinstance(secret_req, dict) else secret_req.secret_list
            )
            results["secrets"] = secret_result
            summary["total_tests"] += 1
            if secret_result["status"] == "OK":
                summary["passed_tests"] += 1
            elif secret_result["status"] == "WARNING":
                summary["warning_tests"] += 1
            else:
                summary["failed_tests"] += 1
        
        # Run metrics check
        if req.include_metrics_check:
            logger.info("Running metrics check")
            metrics_req = req.metrics_request or {}
            metrics_result = await MetricsService.check_metrics(
                resource_id=metrics_req.get("resource_id") if isinstance(metrics_req, dict) else metrics_req.resource_id,
                cpu_threshold=metrics_req.get("cpu_threshold") if isinstance(metrics_req, dict) else metrics_req.cpu_threshold,
                memory_threshold=metrics_req.get("memory_threshold") if isinstance(metrics_req, dict) else metrics_req.memory_threshold
            )
            results["metrics"] = metrics_result
            summary["total_tests"] += 1
            if metrics_result["status"] == "OK":
                summary["passed_tests"] += 1
            elif metrics_result["status"] == "WARNING":
                summary["warning_tests"] += 1
            else:
                summary["failed_tests"] += 1
        
        # Determine overall status
        if summary["failed_tests"] > 0:
            overall_status = "ERROR"
        elif summary["warning_tests"] > 0:
            overall_status = "WARNING"
        else:
            overall_status = "OK"
        
        logger.info(
            f"Run-all completed with status: {overall_status}",
            extra={
                "run_id": run_id,
                "summary": summary
            }
        )
        
        response_data = {
            "run_id": run_id,
            "overall_status": overall_status,
            "summary": summary,
            "details": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return response_builder.success(
            data=response_data,
            message="All tests completed"
        )
    
    except Exception as e:
        logger.error(f"Run-all tests failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_builder.error(
                error="run_all_failed",
                message=str(e),
                status_code=500
            )
        )
