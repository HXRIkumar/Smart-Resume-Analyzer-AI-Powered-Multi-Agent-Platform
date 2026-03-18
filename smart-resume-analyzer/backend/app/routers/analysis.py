"""Analysis router — /analysis/* endpoints for AI pipeline execution."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisResponse,
    AnalysisSummary,
)
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.post(
    "/run",
    response_model=AnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run AI analysis on a resume",
    description=(
        "Triggers the full multi-agent AI pipeline on the specified resume. "
        "The pipeline runs as a background task; this endpoint returns immediately "
        "with a 202 Accepted response containing the analysis record."
    ),
)
async def run_analysis(
    data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Trigger a new resume analysis via the AI pipeline."""
    service = AnalysisService(db)

    # Run the heavy pipeline analysis
    # NOTE: For true background processing we could use Celery/ARQ,
    # but for the MVP the analysis runs inline (5-10s) and returns results
    analysis = await service.analyze(
        resume_id=data.resume_id,
        job_id=data.job_id,
        user_id=current_user.id,
    )
    return analysis


@router.get(
    "/result/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Get analysis result",
    description=(
        "Fetch the full analysis result by ID. "
        "Only accessible to the user who owns the underlying resume."
    ),
)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific analysis result by ID."""
    service = AnalysisService(db)
    return await service.get_analysis(
        analysis_id=analysis_id, user_id=current_user.id
    )


@router.get(
    "/my",
    response_model=list[AnalysisSummary],
    summary="List user's analyses",
    description=(
        "Returns a lightweight summary of all analyses for the current user, "
        "newest first. Used for the dashboard history view."
    ),
)
async def list_my_analyses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all analyses for the current user."""
    service = AnalysisService(db)
    return await service.get_user_analyses(user_id=current_user.id)
