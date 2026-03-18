"""Admin router — /admin/* endpoints requiring admin privileges."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.analysis import AdminAnalyticsResponse, AnalysisSummary
from app.schemas.user import UserResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get(
    "/analytics",
    response_model=AdminAnalyticsResponse,
    summary="Get platform analytics",
    description=(
        "Returns comprehensive platform-wide statistics including total counts, "
        "average scores, score distribution histogram, monthly time-series, "
        "most popular career prediction, and top missing resume sections."
    ),
)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Get platform-wide analytics (admin only)."""
    service = AdminService(db)
    return await service.get_analytics()


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List all users",
    description="Paginated list of all registered users, newest first.",
)
async def list_users(
    skip: int = Query(default=0, ge=0, description="Records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """List all users with pagination (admin only)."""
    service = AdminService(db)
    return await service.get_all_users(skip=skip, limit=limit)


@router.get(
    "/analyses",
    response_model=list[AnalysisSummary],
    summary="List all analyses",
    description="Returns analysis summaries across all users, newest first (max 200).",
)
async def list_all_analyses(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """List all analyses across all users (admin only)."""
    service = AdminService(db)
    return await service.get_all_analyses()
