"""Smart Resume Analyzer — FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import user, resume, job_description, analysis  # noqa: F401
from app.routers import auth, resume as resume_router, analysis as analysis_router, admin, job


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # Startup: create upload directory
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title="Smart Resume Analyzer",
    description="Multi-agent AI resume analysis SaaS platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ───
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(resume_router.router, prefix="/resume", tags=["Resume"])
app.include_router(analysis_router.router, prefix="/analysis", tags=["Analysis"])
app.include_router(job.router, prefix="/job", tags=["Job Descriptions"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
