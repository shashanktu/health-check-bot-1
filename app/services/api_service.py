"""
API check service for testing application endpoints.
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
import httpx

from app.config import settings, get_api_list
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder
from app.utils.http_client import make_concurrent_requests

logger = get_logger(__name__)


class ApiService:
    """Service for API health checks."""
    
    @staticmethod
    async def check_apis(
        api_list: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Check multiple APIs concurrently.
        
        Args:
            api_list: List of API configurations. Uses config if not provided.
        
        Returns:
            Test result with status for each API
        """
        apis = api_list or [
            {"name": "Candidate Info", "method": "GET", "url": "https://tagaibackend-fzbab2ascrdabncf.canadacentral-01.azurewebsites.net/api/get/candidate-info"},
            {"name": "Short Listed Candidates", "method": "GET", "url": "https://tagaibackend-fzbab2ascrdabncf.canadacentral-01.azurewebsites.net/api/get-shortlisted-candidates"},
            {"name": "Get Eng Center", "method": "GET", "url": "tagaibackend-fzbab2ascrdabncf.canadacentral-01.azurewebsites.net/api/get-engcenter-select"},

        ]
        
        if not apis:
            logger.warning("No APIs configured for testing")
            return response_builder.test_result(
                test_name="api_check",
                status="WARNING",
                details={
                    "apis_tested": 0,
                    "apis_passed": 0,
                    "apis_failed": 0
                },
                error_message="No APIs configured"
            )
        
        logger.info(f"Testing {len(apis)} APIs")
        
        # Prepare concurrent requests
        requests = []
        for api in apis:
            try:
                method = api.get("method", "GET").upper()
                url = api.get("url")
                
                if not url:
                    logger.warning(f"API missing URL: {api.get('name', 'unknown')}")
                    continue
                
                requests.append((method, url, {}))
            except Exception as e:
                logger.warning(f"Error preparing API request: {str(e)}")
        
        if not requests:
            return response_builder.test_result(
                test_name="api_check",
                status="ERROR",
                details={
                    "apis_tested": 0,
                    "apis_passed": 0,
                    "apis_failed": len(apis)
                },
                error_message="Failed to prepare API requests"
            )
        
        # Execute concurrent requests
        start_time = time.time()
        responses = await make_concurrent_requests(
            requests,
            timeout=settings.API_TIMEOUT,
            max_retries=settings.API_RETRIES
        )
        total_latency_ms = (time.time() - start_time) * 1000
        
        # Process results
        api_results = []
        passed = 0
        failed = 0
        
        for idx, (api, response) in enumerate(zip(apis, responses)):
            api_name = api.get("name", f"api_{idx}")
            method = api.get("method", "GET").upper()
            url = api.get("url", "")
            expected_status = api.get("expected_status", 200)
            
            try:
                if isinstance(response, Exception):
                    # Request failed
                    api_results.append({
                        "name": api_name,
                        "url": url,
                        "method": method,
                        "status_code": None,
                        "status": "FAIL",
                        "error_message": str(response),
                        "latency_ms": None
                    })
                    failed += 1
                    logger.warning(f"API {api_name} failed: {str(response)}")
                else:
                    # Request succeeded
                    latency_ms = response.elapsed.total_seconds() * 1000
                    status_ok = response.status_code == expected_status
                    
                    api_results.append({
                        "name": api_name,
                        "url": url,
                        "method": method,
                        "status_code": response.status_code,
                        "expected_status": expected_status,
                        "status": "OK" if status_ok else "FAIL",
                        "latency_ms": round(latency_ms, 2),
                        "error_message": None if status_ok else f"Expected {expected_status}, got {response.status_code}"
                    })
                    
                    if status_ok:
                        passed += 1
                        logger.info(f"API {api_name} check passed", extra={"latency_ms": latency_ms})
                    else:
                        failed += 1
                        logger.warning(
                            f"API {api_name} check failed",
                            extra={
                                "expected": expected_status,
                                "got": response.status_code
                            }
                        )
            except Exception as e:
                api_results.append({
                    "name": api_name,
                    "url": url,
                    "method": method,
                    "status_code": None,
                    "status": "FAIL",
                    "error_message": str(e),
                    "latency_ms": None
                })
                failed += 1
                logger.error(f"Error processing API result for {api_name}: {str(e)}")
        
        # Determine overall status
        if failed == 0:
            overall_status = "OK"
        elif failed < len(api_results) / 2:
            overall_status = "WARNING"
        else:
            overall_status = "ERROR"
        
        logger.info(
            "API check completed",
            extra={
                "total": len(api_results),
                "passed": passed,
                "failed": failed,
                "status": overall_status
            }
        )
        
        return response_builder.test_result(
            test_name="api_check",
            status=overall_status,
            details={
                "apis_tested": len(api_results),
                "apis_passed": passed,
                "apis_failed": failed,
                "api_results": api_results
            },
            latency_ms=total_latency_ms
        )
