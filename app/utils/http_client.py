"""
HTTP client utility with retry logic and exponential backoff.
"""

import asyncio
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
import time

from app.utils.logger import get_logger

logger = get_logger(__name__)


class AsyncHttpClient:
    """Async HTTP client with retry logic."""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize HTTP client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make GET request with retry logic.
        
        Args:
            url: Request URL
            headers: Request headers
            **kwargs: Additional arguments for httpx.get
        
        Returns:
            Response object
        
        Raises:
            httpx.RequestError: If all retries fail
        """
        return await self._request("GET", url, headers=headers, **kwargs)
    
    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make POST request with retry logic.
        
        Args:
            url: Request URL
            data: Form data
            json: JSON payload
            headers: Request headers
            **kwargs: Additional arguments for httpx.post
        
        Returns:
            Response object
        """
        return await self._request(
            "POST", url,
            data=data, json=json, headers=headers, **kwargs
        )
    
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with exponential backoff retry.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments for httpx request
        
        Returns:
            Response object
        
        Raises:
            httpx.RequestError: If all retries fail
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                response = await self.client.request(method, url, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                
                logger.info(
                    f"HTTP {method} request successful",
                    extra={
                        "url": url,
                        "status": response.status_code,
                        "latency_ms": elapsed,
                        "attempt": attempt + 1
                    }
                )
                
                return response
            
            except (httpx.RequestError, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"HTTP {method} request failed, retrying in {wait_time}s",
                        extra={
                            "url": url,
                            "attempt": attempt + 1,
                            "error": str(e)
                        }
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"HTTP {method} request failed after {self.max_retries} attempts",
                        extra={
                            "url": url,
                            "error": str(e)
                        }
                    )
        
        raise last_exception or httpx.RequestError("Request failed")


async def make_concurrent_requests(
    requests: list,
    timeout: int = 10,
    max_retries: int = 3
) -> list:
    """
    Make multiple HTTP requests concurrently.
    
    Args:
        requests: List of request tuples (method, url, kwargs)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries per request
    
    Returns:
        List of responses
    """
    async with AsyncHttpClient(timeout=timeout, max_retries=max_retries) as client:
        tasks = []
        for method, url, kwargs in requests:
            if method.upper() == "GET":
                task = client.get(url, **kwargs)
            elif method.upper() == "POST":
                task = client.post(url, **kwargs)
            else:
                task = client._request(method, url, **kwargs)
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
