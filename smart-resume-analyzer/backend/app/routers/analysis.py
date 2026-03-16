"""Analysis router — /analysis/* endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.analysis import AnalysisListResponse, AnalysisRequest, AnalysisResponse, AnalysisSummary
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.post("/run", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_analysis(
    data: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger a new resume analysis via the AI pipeline."""
    service = AnalysisService(db)
    analysis = await service.create_analysis(
        resume_id=data.resume_id,
        job_description_id=data.job_description_id,
        user_id=current_user.id,
    )
    # Run the heavy AI pipeline in the background
    background_tasks.add_task(service.run_pipeline, analysis.id)
    return analysis


@router.get("/", response_model=AnalysisListResponse)
async def list_analyses(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all analyses for the current user."""
    service = AnalysisService(db)
    analyses, total = await service.list_by_user(user_id=current_user.id, skip=skip, limit=limit)
    return AnalysisListResponse(analyses=analyses, total=total)


@router.get("/summary", response_model=AnalysisSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get analysis summary stats for dashboard."""
    service = AnalysisService(db)
    return await service.get_summary(user_id=current_user.id)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific analysis result."""
    service = AnalysisService(db)
    result = await service.get_by_id(analysis_id=analysis_id, user_id=current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return result
