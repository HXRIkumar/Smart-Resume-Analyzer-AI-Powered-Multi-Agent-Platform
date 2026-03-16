"""Admin router — /admin/* endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.user import UserListResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """List all users (admin only)."""
    service = AdminService(db)
    users, total = await service.list_users(skip=skip, limit=limit)
    return UserListResponse(users=users, total=total)


@router.get("/stats")
async def get_platform_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Get platform-wide analytics."""
    service = AdminService(db)
    return await service.get_platform_stats()


@router.delete("/users/{user_id}", status_code=204)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Deactivate a user account."""
    service = AdminService(db)
    await service.deactivate_user(user_id)
