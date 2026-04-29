import logging
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from .config import settings
from .api import api_router
from .database import engine
from .logging_config import configure_logging, request_id_var

configure_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Salesai API",
    description="Backend API for AI-powered sales assistant platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    token = request_id_var.set(request_id)
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled request error",
            extra={"method": request.method, "path": request.url.path},
        )
        raise
    finally:
        request_id_var.reset(token)

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled application exception",
        extra={"method": request.method, "path": request.url.path},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request_id_var.get(),
        },
    )


# Include API routes
app.include_router(api_router, prefix="/api")

if settings.ENABLE_LOCAL_UPLOADS and Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Salesai API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Liveness check that does not touch dependencies."""
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check():
    """Readiness check that verifies database connectivity."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready"}
