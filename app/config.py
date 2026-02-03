"""
Configuration module for Smoke Test Bot.
Loads environment variables and provides centralized configuration.
"""

import os
import json
from typing import List, Dict, Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(extra="ignore", env_file=".env")
    
    # Service configuration
    SERVICE_NAME: str = "smoke-test-bot"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://user:password@localhost:5432/smoke_test_db"
    )
    SAMPLE_QUERY: str = os.getenv("SAMPLE_QUERY", "SELECT 1")
    DB_TIMEOUT: int = int(os.getenv("DB_TIMEOUT", "10"))
    DB_RETRIES: int = int(os.getenv("DB_RETRIES", "3"))
    
    # API Check configuration
    API_LIST_JSON: str = os.getenv(
        "API_LIST_JSON",
        os.getenv(
            "API_LIST",
            json.dumps([
                {
                    "name": "example_api",
                    "method": "GET",
                    "url": "https://api.example.com/health",
                    "expected_status": 200,
                }
            ]),
        ),
    )
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "10"))
    API_RETRIES: int = int(os.getenv("API_RETRIES", "2"))
    
    # Azure KeyVault configuration
    AZURE_KEYVAULT_NAME: str = os.getenv("AZURE_KEYVAULT_NAME", "my-keyvault")
    AZURE_SECRET_LIST_JSON: str = os.getenv(
        "AZURE_SECRET_LIST_JSON",
        os.getenv(
            "AZURE_SECRETS_LIST",
            os.getenv(
                "AZURE_SECRET_LIST",
                json.dumps(["secret1", "secret2"]),
            ),
        ),
    )
    AZURE_CLIENT_ID: Optional[str] = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: Optional[str] = os.getenv("AZURE_CLIENT_SECRET")
    AZURE_TENANT_ID: Optional[str] = os.getenv("AZURE_TENANT_ID")
    AZURE_TIMEOUT: int = int(os.getenv("AZURE_TIMEOUT", "10"))

    # Azure subscription/resource identifiers
    AZURE_SUBSCRIPTION_ID: Optional[str] = os.getenv("AZURE_SUBSCRIPTION_ID")
    AZURE_RESOURCE_GROUP: Optional[str] = os.getenv("AZURE_RESOURCE_GROUP")
    AZURE_WEBAPP_NAME: Optional[str] = os.getenv("AZURE_WEBAPP_NAME", os.getenv("AZURE_VM_NAME"))
    
    # Azure Metrics configuration
    VM_RESOURCE_ID: Optional[str] = os.getenv("VM_RESOURCE_ID")
    WEBAPP_RESOURCE_ID: Optional[str] = os.getenv("WEBAPP_RESOURCE_ID")
    METRIC_THRESHOLD_CPU: int = int(os.getenv("METRIC_THRESHOLD_CPU", "80"))
    METRIC_THRESHOLD_MEMORY: int = int(os.getenv("METRIC_THRESHOLD_MEMORY", "500"))
    METRICS_TIMEOUT: int = int(os.getenv("METRICS_TIMEOUT", "15"))
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"


# Global settings instance
settings = Settings()


def get_api_list() -> List[Dict]:
    """Parse and return API list from JSON configuration."""
    try:
        return json.loads(settings.API_LIST_JSON)
    except json.JSONDecodeError:
        return []


def get_azure_secrets_list() -> List[str]:
    """Parse and return Azure secret list from JSON configuration."""
    try:
        return json.loads(settings.AZURE_SECRET_LIST_JSON)
    except json.JSONDecodeError:
        return []


def get_resource_id() -> Optional[str]:
    """Return a resource ID to query metrics for.

    Priority order:
      1. settings.WEBAPP_RESOURCE_ID
      2. settings.VM_RESOURCE_ID
      3. Build a Microsoft.Web/sites resource id from AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP and AZURE_WEBAPP_NAME

    Returns None if no usable identifiers are present.
    """
    if settings.WEBAPP_RESOURCE_ID:
        return settings.WEBAPP_RESOURCE_ID

    if settings.VM_RESOURCE_ID:
        return settings.VM_RESOURCE_ID

    if (
        settings.AZURE_SUBSCRIPTION_ID
        and settings.AZURE_RESOURCE_GROUP
        and settings.AZURE_WEBAPP_NAME
    ):
        return (
            f"/subscriptions/{settings.AZURE_SUBSCRIPTION_ID}"
            f"/resourceGroups/{settings.AZURE_RESOURCE_GROUP}"
            f"/providers/Microsoft.Web/sites/{settings.AZURE_WEBAPP_NAME}"
        )

    return None
