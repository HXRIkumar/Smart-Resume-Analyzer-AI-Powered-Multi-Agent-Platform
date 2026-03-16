"""Admin service — admin analytics queries."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import AnalysisResult
from app.utils.exceptions import NotFoundError


class AdminService:
    """Admin-level analytics and user management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, skip: int = 0, limit: int = 50) -> tuple[list[User], int]:
        """List all users with pagination."""
        query = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        count_result = await self.db.execute(select(func.count(User.id)))
        total = count_result.scalar() or 0
        return users, total

    async def get_platform_stats(self) -> dict:
        """Get platform-wide analytics."""
        total_users = (await self.db.execute(select(func.count(User.id)))).scalar() or 0
        total_resumes = (await self.db.execute(select(func.count(Resume.id)))).scalar() or 0
        total_analyses = (await self.db.execute(select(func.count(AnalysisResult.id)))).scalar() or 0
        avg_score = (
            await self.db.execute(
                select(func.avg(AnalysisResult.overall_score)).where(
                    AnalysisResult.status == "completed"
                )
            )
        ).scalar()

        return {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "total_analyses": total_analyses,
            "average_score": round(float(avg_score or 0), 1),
        }

    async def deactivate_user(self, user_id: int) -> None:
        """Deactivate a user account."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        user.is_active = False
        await self.db.flush()
