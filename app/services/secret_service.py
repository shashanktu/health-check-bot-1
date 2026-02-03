"""
Azure KeyVault secret check service.
"""

import time
from typing import Optional, Dict, Any, List

from app.config import settings, get_azure_secrets_list
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder

logger = get_logger(__name__)


class SecretService:
    """Service for Azure KeyVault secret checks."""
    
    @staticmethod
    async def check_secrets(
        keyvault_name: Optional[str] = None,
        secret_list: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check Azure KeyVault secrets.
        
        Args:
            keyvault_name: KeyVault name. Uses config if not provided.
            secret_list: List of secret names. Uses config if not provided.
        
        Returns:
            Test result with status for each secret
        """
        vault_name = keyvault_name or "certsigning"
        secrets = secret_list or ["gemini-api-key", "secret1", "secret2"]
        if not secrets:
            logger.warning("No secrets configured for testing")
            return response_builder.test_result(
                test_name="secret_check",
                status="WARNING",
                details={
                    "total_secrets": 0,
                    "found_secrets": 0,
                    "secret_results": []
                },
                error_message="No secrets configured"
            )
        start_time = time.time()
        logger.info(f"Checking {len(secrets)} secrets in KeyVault: {vault_name}")
        
        # Try to import Azure SDK
        try:
            from azure.identity import ClientSecretCredential, DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
        except ImportError:
            latency_ms = (time.time() - start_time) * 1000
            logger.error("Azure SDK not installed")
            
            return response_builder.test_result(
                test_name="secret_check",
                status="ERROR",
                details={
                    "total_secrets": len(secrets),
                    "found_secrets": 0,
                    "secret_results": []
                },
                error_message="Azure SDK not installed",
                latency_ms=latency_ms
            )
        
        try:
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
            vault_url = f"https://{vault_name}.vault.azure.net"
            client = SecretClient(vault_url=vault_url, credential=credential)
            
            # Check each secret
            secret_results = []
            found_count = 0
            
            for secret_name in secrets:
                try:
                    logger.debug(f"Checking secret: {secret_name}")
                    secret = client.get_secret(secret_name)
                    
                    secret_results.append({
                        "name": secret_name,
                        "status": "FOUND",
                        "error_message": None
                    })
                    found_count += 1
                    logger.info(f"Secret found: {secret_name}")
                
                except Exception as e:
                    error_msg = str(e)
                    
                    if "SecretNotFound" in str(type(e)) or "ResourceNotFound" in error_msg:
                        status = "MISSING"
                    elif "Forbidden" in error_msg or "permission" in error_msg.lower():
                        status = "PERMISSION_DENIED"
                    else:
                        status = "PERMISSION_DENIED"
                    
                    secret_results.append({
                        "name": secret_name,
                        "status": status,
                        "error_message": error_msg
                    })
                    
                    logger.warning(f"Secret check failed for {secret_name}: {error_msg}")
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Determine overall status
            if found_count == len(secrets):
                overall_status = "OK"
            elif found_count == 0:
                overall_status = "ERROR"
            else:
                overall_status = "WARNING"
            
            logger.info(
                "Secret check completed",
                extra={
                    "total": len(secrets),
                    "found": found_count,
                    "status": overall_status
                }
            )
            
            return response_builder.test_result(
                test_name="secret_check",
                status=overall_status,
                details={
                    "total_secrets": len(secrets),
                    "found_secrets": found_count,
                    "secret_results": secret_results
                },
                latency_ms=latency_ms
            )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"KeyVault authentication error: {str(e)}"
            logger.error("Secret check failed", extra={"error": error_msg})
            
            return response_builder.test_result(
                test_name="secret_check",
                status="ERROR",
                details={
                    "total_secrets": len(secrets),
                    "found_secrets": 0,
                    "secret_results": []
                },
                error_message=error_msg,
                latency_ms=latency_ms
            )
