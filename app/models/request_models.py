"""
Pydantic request models for API endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any


class ApiCheckRequest(BaseModel):
    """Request model for API check endpoint."""
    
    api_list: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of APIs to check. If not provided, uses API_LIST from config."
    )


class DatabaseCheckRequest(BaseModel):
    """Request model for database check endpoint."""
    
    database_url: Optional[str] = Field(
        None,
        description="Database URL. If not provided, uses DATABASE_URL from config."
    )
    query: Optional[str] = Field(
        None,
        description="Query to execute. If not provided, uses SAMPLE_QUERY from config."
    )


class SecretCheckRequest(BaseModel):
    """Request model for secret check endpoint."""
    
    keyvault_name: Optional[str] = Field(
        None,
        description="KeyVault name. If not provided, uses AZURE_KEYVAULT_NAME from config."
    )
    secret_list: Optional[List[str]] = Field(
        None,
        description="List of secret names. If not provided, uses AZURE_SECRET_LIST from config."
    )


class MetricsCheckRequest(BaseModel):
    """Request model for metrics check endpoint."""
    
    resource_id: Optional[str] = Field(
        None,
        description="Azure VM resource ID. If not provided, uses VM_RESOURCE_ID from config."
    )
    cpu_threshold: Optional[int] = Field(
        None,
        description="CPU threshold percentage. If not provided, uses METRIC_THRESHOLD_CPU from config."
    )
    memory_threshold: Optional[int] = Field(
        None,
        description="Memory threshold in MB. If not provided, uses METRIC_THRESHOLD_MEMORY from config."
    )


class RunAllRequest(BaseModel):
    """Request model for run-all endpoint."""
    
    include_db_check: bool = Field(True, description="Include database check")
    include_api_check: bool = Field(True, description="Include API check")
    include_secret_check: bool = Field(True, description="Include secret check")
    include_metrics_check: bool = Field(True, description="Include metrics check")
    db_request: Optional[DatabaseCheckRequest] = Field(None, description="Database check configuration")
    api_request: Optional[ApiCheckRequest] = Field(None, description="API check configuration")
    secret_request: Optional[SecretCheckRequest] = Field(None, description="Secret check configuration")
    metrics_request: Optional[MetricsCheckRequest] = Field(None, description="Metrics check configuration")
