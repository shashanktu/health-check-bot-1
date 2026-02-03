"""
Pydantic response models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class TestDetail(BaseModel):
    """Individual test result detail."""
    
    test_name: str = Field(..., description="Name of the test")
    status: str = Field(..., description="Test status: OK, WARNING, ERROR, CRITICAL")
    details: Dict[str, Any] = Field(default_factory=dict, description="Test-specific details")
    error_message: Optional[str] = Field(None, description="Error message if any")
    latency_ms: Optional[float] = Field(None, description="Operation latency in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the test")


class ApiCheckResponse(BaseModel):
    """Response model for individual API check."""
    
    name: str = Field(..., description="API name")
    url: str = Field(..., description="API URL")
    method: str = Field(..., description="HTTP method")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    status: str = Field(..., description="Status: OK or FAIL")
    latency_ms: float = Field(..., description="Latency in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if any")


class DatabaseCheckResponse(BaseModel):
    """Response model for database check."""
    
    status: str = Field(..., description="Status: UP or DOWN")
    latency_ms: float = Field(..., description="Query latency in milliseconds")
    query_result_summary: Optional[str] = Field(None, description="Summary of query result")
    error_message: Optional[str] = Field(None, description="Error message if any")


class SecretCheckDetail(BaseModel):
    """Individual secret check result."""
    
    name: str = Field(..., description="Secret name")
    status: str = Field(..., description="Status: FOUND, MISSING, PERMISSION_DENIED")
    error_message: Optional[str] = Field(None, description="Error message if any")


class SecretCheckResponse(BaseModel):
    """Response model for secret check."""
    
    overall_status: str = Field(..., description="Status: OK, WARNING, ERROR")
    secrets: List[SecretCheckDetail] = Field(..., description="List of secret check results")
    total_secrets: int = Field(..., description="Total secrets checked")
    found_secrets: int = Field(..., description="Number of secrets found")
    error_message: Optional[str] = Field(None, description="Overall error message if any")


class MetricValue(BaseModel):
    """Individual metric value."""
    
    metric_name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    status: str = Field(..., description="Status: OK, WARNING, CRITICAL")


class MetricsCheckResponse(BaseModel):
    """Response model for metrics check."""
    
    status: str = Field(..., description="Overall status: OK, WARNING, CRITICAL")
    cpu_usage: Optional[MetricValue] = Field(None, description="CPU usage metric")
    memory_usage: Optional[MetricValue] = Field(None, description="Memory usage metric")
    error_message: Optional[str] = Field(None, description="Error message if any")


class RunAllResponse(BaseModel):
    """Response model for run-all endpoint."""
    
    run_id: str = Field(..., description="Unique run ID")
    overall_status: str = Field(..., description="Overall status: OK, WARNING, ERROR")
    summary: Dict[str, Any] = Field(..., description="Summary of all test results")
    details: Dict[str, Any] = Field(..., description="Detailed results for each test")
    timestamp: datetime = Field(..., description="Timestamp of the run")


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Service status: healthy, unhealthy")
    service_name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Timestamp")
