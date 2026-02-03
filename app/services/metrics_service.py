"""
Azure Monitor metrics check service.
"""

import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.config import settings, get_resource_id
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder

logger = get_logger(__name__)


class MetricsService:
    """Service for Azure Monitor metrics checks."""
    
    @staticmethod
    async def check_metrics(
        resource_id: Optional[str] = None,
        cpu_threshold: Optional[int] = None,
        memory_threshold: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Check Azure VM metrics (CPU and Memory).
        
        Args:
            resource_id: Azure VM resource ID. Uses config if not provided.
            cpu_threshold: CPU threshold percentage. Uses config if not provided.
            memory_threshold: Memory threshold in MB. Uses config if not provided.
        
        Returns:
            Test result with CPU and memory metrics
        """
        res_id = resource_id or "/subscriptions/46269e09-e1e1-4067-af90-78fd27b1b64d/resourceGroups/ba-agent-rg/providers/Microsoft.Web/sites/backend-uw-workbench"
        cpu_thresh = cpu_threshold or 75
        mem_thresh = memory_threshold or 80
        start_time = time.time()
        logger.info(f"Checking metrics for resource: {res_id}")
        
        # Try to import Azure SDK
        try:
            from azure.identity import ClientSecretCredential, DefaultAzureCredential
            from azure.mgmt.monitor import MonitorManagementClient
        except ImportError:
            latency_ms = (time.time() - start_time) * 1000
            logger.error("Azure SDK not installed")
            
            return response_builder.test_result(
                test_name="metrics_check",
                status="ERROR",
                details={
                    "cpu_usage": None,
                    "memory_usage": None
                },
                error_message="Azure SDK not installed",
                latency_ms=latency_ms
            )
        
        try:
            # Extract subscription ID from resource ID
            parts = res_id.split("/")
            subscription_id = parts[2] if len(parts) > 2 else None
            
            if not subscription_id:
                raise ValueError("Invalid resource ID format")
            
            # Initialize credential
            credential = None
            if settings.AZURE_CLIENT_ID and settings.AZURE_CLIENT_SECRET and settings.AZURE_TENANT_ID:
                logger.info("Using ClientSecretCredential for authentication")
                credential = ClientSecretCredential(
                    client_id=settings.AZURE_CLIENT_ID,
                    client_secret=settings.AZURE_CLIENT_SECRET,
                    tenant_id=settings.AZURE_TENANT_ID
                )
            else:
                logger.info("Using DefaultAzureCredential for authentication")
                credential = DefaultAzureCredential()
            
            # Create client
            client = MonitorManagementClient(credential, subscription_id)
            
            # Get CPU metric
            cpu_metric = None
            cpu_status = "OK"
            try:
                cpu_metric = await MetricsService._get_metric(
                    client,
                    res_id,
                    "Percentage CPU"
                )
                
                if cpu_metric is not None:
                    if cpu_metric > cpu_thresh:
                        cpu_status = "CRITICAL" if cpu_metric > cpu_thresh * 1.5 else "WARNING"
                    
                    logger.info(
                        f"CPU metric retrieved: {cpu_metric}%",
                        extra={"threshold": cpu_thresh, "status": cpu_status}
                    )
            
            except Exception as e:
                logger.warning(f"Failed to get CPU metric: {str(e)}")
            
            # Get Memory metric
            memory_metric = None
            memory_status = "OK"
            try:
                memory_metric = await MetricsService._get_metric(
                    client,
                    res_id,
                    "Available Memory Bytes"
                )
                
                if memory_metric is not None:
                    # Convert bytes to MB
                    memory_mb = memory_metric / (1024 * 1024)
                    
                    if memory_mb < mem_thresh:
                        memory_status = "CRITICAL" if memory_mb < mem_thresh * 0.5 else "WARNING"
                    
                    logger.info(
                        f"Memory metric retrieved: {memory_mb:.2f}MB",
                        extra={"threshold": mem_thresh, "status": memory_status}
                    )
                
            except Exception as e:
                logger.warning(f"Failed to get memory metric: {str(e)}")
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Determine overall status
            overall_status = "OK"
            if cpu_status == "CRITICAL" or memory_status == "CRITICAL":
                overall_status = "CRITICAL"
            elif cpu_status == "WARNING" or memory_status == "WARNING":
                overall_status = "WARNING"
            
            details = {}
            if cpu_metric is not None:
                details["cpu_usage"] = {
                    "value": round(cpu_metric, 2),
                    "unit": "percentage",
                    "threshold": cpu_thresh,
                    "status": cpu_status
                }
            
            if memory_metric is not None:
                memory_mb = memory_metric / (1024 * 1024)
                details["memory_usage"] = {
                    "value": round(memory_mb, 2),
                    "unit": "MB",
                    "threshold": mem_thresh,
                    "status": memory_status
                }
            
            logger.info(
                "Metrics check completed",
                extra={
                    "overall_status": overall_status,
                    "cpu_status": cpu_status,
                    "memory_status": memory_status
                }
            )
            
            return response_builder.test_result(
                test_name="metrics_check",
                status=overall_status,
                details=details,
                latency_ms=latency_ms
            )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"Metrics check error: {str(e)}"
            logger.error("Metrics check failed", extra={"error": error_msg})
            
            return response_builder.test_result(
                test_name="metrics_check",
                status="ERROR",
                details={},
                error_message=error_msg,
                latency_ms=latency_ms
            )
    
    @staticmethod
    async def _get_metric(
        client,
        resource_id: str,
        metric_name: str
    ) -> Optional[float]:
        """
        Get a specific metric from Azure Monitor.
        
        Args:
            client: MonitorManagementClient instance
            resource_id: Azure resource ID
            metric_name: Metric name to retrieve
        
        Returns:
            Latest metric value or None if not available
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            metrics = client.metrics.list(
                resource_id=resource_id,
                timespan=f"{start_time.isoformat()}Z/{end_time.isoformat()}Z",
                metric_names=[metric_name],
                aggregation="Average",
                interval="PT1M"
            )
            
            for metric in metrics.value:
                if metric.timeseries:
                    # Get the latest data point
                    for timeseries in metric.timeseries:
                        if timeseries.data:
                            latest_data = timeseries.data[-1]
                            if hasattr(latest_data, 'average') and latest_data.average is not None:
                                return latest_data.average
            
            return None
        
        except Exception as e:
            logger.debug(f"Error getting metric {metric_name}: {str(e)}")
            return None
