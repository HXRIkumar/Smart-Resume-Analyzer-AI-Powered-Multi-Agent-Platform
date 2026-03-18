"""Smart Resume Analyzer — FastAPI Application.

Production-grade entry point with CORS middleware, X-Request-ID injection,
global exception handlers, health check with DB ping, and lifespan
management for the database connection pool.
"""

import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, check_db_health, engine
from app.models import user, resume, job_description, analysis  # noqa: F401
from app.routers import (
    admin,
    analysis as analysis_router,
    auth,
    job,
    resume as resume_router,
)

logger = logging.getLogger(__name__)


# ─── Lifespan ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown.

    Startup:
        - Create upload directory
        - Create DB tables (dev convenience — Alembic handles migrations)
    Shutdown:
        - Dispose the async engine connection pool
    """
    # Startup
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Upload directory ready: %s", settings.UPLOAD_DIR)

    # Create tables (safe no-op if they already exist)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    await engine.dispose()
    logger.info("Database connection pool disposed")


# ─── App Instance ────────────────────────────────────────────────────────────

app = FastAPI(
    title="Smart Resume Analyzer API",
    description=(
        "Multi-agent AI-powered resume analysis platform. "
        "Upload resumes, run AI analysis pipelines, get ATS scores, "
        "skills gap analysis, career predictions, and actionable feedback."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─── CORS Middleware ─────────────────────────────────────────────────────────

allowed_origins = [settings.FRONTEND_URL]
if "localhost:5173" not in settings.FRONTEND_URL:
    allowed_origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── X-Request-ID Middleware ─────────────────────────────────────────────────

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Inject X-Request-ID header into every request/response cycle.

    If the client sends an X-Request-ID header, it is preserved.
    Otherwise a new UUID4 is generated.
    """
    request_id = request.headers.get("x-request-id", uuid.uuid4().hex)
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ─── Global Exception Handlers ──────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """422 — return field-level validation errors in a clean format."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", ""),
            "type": error.get("type", ""),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standard HTTP error → JSON with request_id."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """500 — catch-all for unhandled exceptions with request_id."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(
        "Unhandled exception [request_id=%s]: %s", request_id, str(exc)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )


# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(resume_router.router, prefix="/resume", tags=["Resume"])
app.include_router(analysis_router.router, prefix="/analysis", tags=["Analysis"])
app.include_router(job.router, prefix="/job", tags=["Job Descriptions"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Returns application health status including DB connectivity and version.",
)
async def health_check():
    """Health check endpoint with DB connectivity test."""
    db_health = await check_db_health()
    return {
        "status": "ok",
        "version": "1.0.0",
        "db_connected": db_health.get("status") == "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
