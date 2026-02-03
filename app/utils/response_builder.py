"""
Consistent response builder for all API endpoints.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
import uuid


class ResponseBuilder:
    """Build standardized API responses."""
    
    @staticmethod
    def success(
        data: Any,
        message: str = "Success",
        status_code: int = 200
    ) -> Dict[str, Any]:
        """
        Build a success response.
        
        Args:
            data: Response payload
            message: Success message
            status_code: HTTP status code
        
        Returns:
            Standardized success response
        """
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    
    @staticmethod
    def error(
        error: str,
        message: str = "An error occurred",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build an error response.
        
        Args:
            error: Error type/code
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        
        Returns:
            Standardized error response
        """
        return {
            "status": "error",
            "error": error,
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    
    @staticmethod
    def test_result(
        test_name: str,
        status: str,  # "OK", "WARNING", "ERROR", "CRITICAL"
        details: Dict[str, Any],
        error_message: Optional[str] = None,
        latency_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Build a standardized test result.
        
        Args:
            test_name: Name of the test
            status: Test status
            details: Test-specific details
            error_message: Error message if any
            latency_ms: Operation latency in milliseconds
        
        Returns:
            Standardized test result
        """
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error_message:
            result["error_message"] = error_message
        
        if latency_ms is not None:
            result["latency_ms"] = round(latency_ms, 2)
        
        return result


# Singleton instance
response_builder = ResponseBuilder()
