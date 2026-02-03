"""
Database check service for PostgreSQL connectivity and query execution.
"""

import asyncio
import time
from typing import Optional, Dict, Any
import asyncpg

from app.config import settings
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder

logger = get_logger(__name__)


class DatabaseService:
    """Service for database health checks."""
    
    @staticmethod
    async def check_database(
        database_url: Optional[str] = None,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check database connectivity and execute a test query.
        
        Args:
            database_url: Database connection URL. Uses config if not provided.
            query: Query to execute. Uses config if not provided.
        
        Returns:
            Test result with status, latency, and query result
        """
        db_url = database_url or "postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require"
        test_query = query or "SELECT 1"
        start_time = time.time()
        connection = None
        try:
            logger.info("Attempting database connection", extra={"database_url": db_url})
            # Create connection with timeout
            try:
                connection = await asyncio.wait_for(
                    asyncpg.connect(db_url),
                    timeout=settings.DB_TIMEOUT
                )
            except asyncio.TimeoutError:
                latency_ms = (time.time() - start_time) * 1000
                error_msg = f"Connection timeout after {settings.DB_TIMEOUT} seconds"
                logger.error("Database connection timeout", extra={"latency_ms": latency_ms})
                return response_builder.test_result(
                    test_name="database_check",
                    status="DOWN",
                    details={
                        "connection_status": "timeout"
                    },
                    error_message=error_msg,
                    latency_ms=latency_ms
                )
            # Execute test query
            logger.info("Executing test query", extra={"query": test_query})
            query_start = time.time()
            try:
                result = await asyncio.wait_for(
                    connection.fetchval(test_query),
                    timeout=settings.DB_TIMEOUT
                )
            except asyncio.TimeoutError:
                query_latency_ms = (time.time() - query_start) * 1000
                total_latency_ms = (time.time() - start_time) * 1000
                error_msg = f"Query timeout after {settings.DB_TIMEOUT} seconds"
                logger.error("Database query timeout", extra={"latency_ms": total_latency_ms})
                return response_builder.test_result(
                    test_name="database_check",
                    status="DOWN",
                    details={
                        "connection_status": "connected",
                        "query_status": "timeout"
                    },
                    error_message=error_msg,
                    latency_ms=total_latency_ms
                )
            
            total_latency_ms = (time.time() - start_time) * 1000
            
            logger.info(
                "Database check successful",
                extra={
                    "latency_ms": total_latency_ms,
                    "result": str(result)
                }
            )
            
            return response_builder.test_result(
                test_name="database_check",
                status="UP",
                details={
                    "connection_status": "connected",
                    "query_status": "executed",
                    "query_result_summary": str(result)
                },
                latency_ms=total_latency_ms
            )
        
        except asyncpg.InvalidCatalogNameError as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"Invalid database name: {str(e)}"
            logger.error("Database connection error", extra={"error": error_msg})
            
            return response_builder.test_result(
                test_name="database_check",
                status="DOWN",
                details={
                    "connection_status": "error",
                    "error_type": "invalid_catalog"
                },
                error_message=error_msg,
                latency_ms=latency_ms
            )
        
        except asyncpg.AuthenticationFailedError as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"Authentication failed: {str(e)}"
            logger.error("Database authentication error", extra={"error": error_msg})
            
            return response_builder.test_result(
                test_name="database_check",
                status="DOWN",
                details={
                    "connection_status": "error",
                    "error_type": "authentication_failed"
                },
                error_message=error_msg,
                latency_ms=latency_ms
            )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(
                "Database check failed",
                extra={
                    "error": error_msg,
                    "error_type": type(e).__name__,
                    "latency_ms": latency_ms
                }
            )
            
            return response_builder.test_result(
                test_name="database_check",
                status="DOWN",
                details={
                    "connection_status": "error",
                    "error_type": type(e).__name__
                },
                error_message=error_msg,
                latency_ms=latency_ms
            )
        
        finally:
            # Close connection
            if connection:
                try:
                    await connection.close()
                    logger.debug("Database connection closed")
                except Exception as e:
                    logger.warning(f"Error closing database connection: {str(e)}")
