"""
FastAPI application entry point.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

from app.config import settings
from app.utils.logger import get_logger
from app.utils.response_builder import response_builder
from app.routers import db_check, api_check, secret_check, metrics_check, run_all
import requests as request

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.SERVICE_VERSION,
    description="Backend service for performing smoke tests",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    request_id = str(uuid.uuid4())
    logger.error(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
            "error_type": type(exc).__name__
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_builder.error(
            error="internal_server_error",
            message="An unexpected error occurred",
            status_code=500,
            details={"request_id": request_id}
        )
    )


# Include routers
from app.routers import test_impact, genai
from fastapi.staticfiles import StaticFiles
app.include_router(db_check.router)
app.include_router(api_check.router)
app.include_router(secret_check.router)
app.include_router(metrics_check.router)
app.include_router(run_all.router)
app.include_router(test_impact.router)
app.include_router(genai.router)
app.mount("/playwright-report", StaticFiles(directory="playwright-report"), name="playwright-report")
@app.get("/commits/latest", tags=["commits"])
async def get_latest_commit():
    """
    Returns latest commit info (stub for frontend integration)
    """
    url="https://api.github.com/repos/mohansai001/tag-frontend/commits?sha=master"  # Replace with actual repo
    api_key="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"  # Replace with actual API key
    response=request.get(url, headers={"Authorization": f"token {api_key}"})
            # st.chat_message("assistant").write("Fetching latest commits...")
            # st.chat_message("assistant").write(response.json())
    details=response.json()[0]['commit']
    sha=response.json()[0]['sha']
    commit_url="https://api.github.com/repos/mohansai001/tag-frontend/commits/"+sha
    response_commit=request.get(commit_url, headers={"Authorization": f"token {api_key}"})
            # st.write(response_commit.json())
    # st.write(len(response_commit.json()['files']))
    file_name=""
    if len(response_commit.json()['files'])>1:
                for i in range(len(response_commit.json()['files'])):
                    file_name+=response_commit.json()['files'][i]['filename']+", "
    if len(response_commit.json()['files'])==1:
                file_name=response_commit.json()['files'][0]['filename']
            # st.chat_message("assistant").write(response_commit.json()['files'][0]['filename'])
            # st.chat_message("assistant").write(f"Latest commit SHA: {sha}")
    # st.chat_message("assistant").write(f"Below are the latest commit details:\n- Author: {details['author']['name']}\n- Date: {details['author']['date']}\n- Message: {details['message']}\n- Files Changed: {file_name}")

    # TODO: Replace with real git integration or API call
    return {
        "author":details['author']['name'],
        "date": details['author']['date'],
        "message": details['message'],
        "files_changed": file_name,
        
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service health status
    """
    logger.debug("Health check requested")
    
    return response_builder.success(
        data={
            "status": "healthy",
            "service_name": settings.SERVICE_NAME,
            "version": settings.SERVICE_VERSION,
            "timestamp": datetime.utcnow().isoformat()
        },
        message="Service is healthy"
    )


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with service information.
    
    Returns:
        Service information and available endpoints
    """
    return response_builder.success(
        data={
            "service_name": settings.SERVICE_NAME,
            "version": settings.SERVICE_VERSION,
            "description": "Smoke Test Bot Backend",
            "endpoints": {
                "health": "GET /health",
                "run_all": "POST /run-all",
                "database_check": "POST /test/db",
                "api_check": "POST /test/apis",
                "secret_check": "POST /test/secrets",
                "metrics_check": "POST /test/metrics",
                "docs": "GET /docs",
                "redoc": "GET /redoc"
            }
        },
        message="Smoke Test Bot Backend"
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(
        f"Application starting: {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}",
        extra={
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info(f"Application shutting down: {settings.SERVICE_NAME}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
