"""Admin service — platform analytics and user management.

Provides aggregate statistics for the admin dashboard including
score distributions, time-series data, and missing section analysis.
"""

import logging
from collections import Counter
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import AnalysisResult
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import AdminAnalyticsResponse, MonthlyCount
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)


class AdminService:
    """Admin-level analytics queries and user management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_analytics(self) -> AdminAnalyticsResponse:
        """Compute platform-wide analytics for the admin dashboard.

        Returns:
            AdminAnalyticsResponse with total counts, averages,
            score histogram, time-series, and missing section data.
        """
        # ── Total counts ─────────────────────────────────────────────────
        total_users = (
            await self.db.execute(select(func.count(User.id)))
        ).scalar() or 0

        total_resumes = (
            await self.db.execute(select(func.count(Resume.id)))
        ).scalar() or 0

        total_applications = (
            await self.db.execute(select(func.count(AnalysisResult.id)))
        ).scalar() or 0

        # ── Average resume score ─────────────────────────────────────────
        avg_score_raw = (
            await self.db.execute(
                select(func.avg(AnalysisResult.resume_score))
            )
        ).scalar()
        avg_resume_score = round(float(avg_score_raw or 0), 1)

        # ── Most popular career ──────────────────────────────────────────
        most_popular_career = await self._get_most_popular_career()

        # ── Applications over time (last 12 months) ──────────────────────
        applications_over_time = await self._get_applications_over_time()

        # ── Score distribution ───────────────────────────────────────────
        score_distribution = await self._get_score_distribution()

        # ── Top missing sections ─────────────────────────────────────────
        top_missing_sections = await self._get_top_missing_sections()

        return AdminAnalyticsResponse(
            total_users=total_users,
            total_resumes=total_resumes,
            total_applications=total_applications,
            avg_resume_score=avg_resume_score,
            most_popular_career=most_popular_career,
            applications_over_time=applications_over_time,
            score_distribution=score_distribution,
            top_missing_sections=top_missing_sections,
            conversion_rate=30.0,  # placeholder — expand later
        )

    async def get_all_users(
        self, skip: int = 0, limit: int = 50
    ) -> list[User]:
        """Return paginated list of all users, newest first.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of User models.
        """
        result = await self.db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_analyses(self) -> list[AnalysisResult]:
        """Return all analyses across all users, newest first.

        Returns:
            List of AnalysisResult models.
        """
        result = await self.db.execute(
            select(AnalysisResult)
            .order_by(AnalysisResult.created_at.desc())
            .limit(200)
        )
        return list(result.scalars().all())

    # ─── Private Helpers ─────────────────────────────────────────────────

    async def _get_most_popular_career(self) -> str:
        """Extract the most frequently predicted career role.

        Reads career_predictions JSON from all analyses and counts
        the top-1 prediction role across all records.

        Returns:
            Most popular career role name, or empty string.
        """
        result = await self.db.execute(
            select(AnalysisResult.career_predictions)
            .where(AnalysisResult.career_predictions.isnot(None))
            .limit(500)
        )
        rows = result.scalars().all()

        counter: Counter[str] = Counter()
        for predictions in rows:
            if isinstance(predictions, dict):
                preds = predictions.get("predictions", [])
                if preds and isinstance(preds, list) and len(preds) > 0:
                    top_role = preds[0].get("role", "")
                    if top_role:
                        counter[top_role] += 1

        if counter:
            return counter.most_common(1)[0][0]
        return ""

    async def _get_applications_over_time(self) -> list[MonthlyCount]:
        """Count analyses grouped by month for the last 12 months.

        Returns:
            List of MonthlyCount entries (month string + count).
        """
        result = await self.db.execute(
            select(
                func.to_char(AnalysisResult.created_at, "YYYY-MM").label("month"),
                func.count(AnalysisResult.id).label("count"),
            )
            .group_by("month")
            .order_by("month")
            .limit(12)
        )
        rows = result.all()
        return [
            MonthlyCount(month=row.month, count=row.count)
            for row in rows
        ]

    async def _get_score_distribution(self) -> dict[str, int]:
        """Compute a histogram of resume scores in 5 buckets.

        Buckets: 0-20, 21-40, 41-60, 61-80, 81-100.

        Returns:
            Dict mapping bucket label → count.
        """
        result = await self.db.execute(
            select(AnalysisResult.resume_score)
        )
        scores = [row for row in result.scalars().all()]

        distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for score in scores:
            if score <= 20:
                distribution["0-20"] += 1
            elif score <= 40:
                distribution["21-40"] += 1
            elif score <= 60:
                distribution["41-60"] += 1
            elif score <= 80:
                distribution["61-80"] += 1
            else:
                distribution["81-100"] += 1

        return distribution

    async def _get_top_missing_sections(self) -> list[dict]:
        """Aggregate the most commonly missing resume sections.

        Reads the improvements list from all analyses and counts
        section-related improvement mentions.

        Returns:
            List of {section, count} dicts, sorted by count descending.
        """
        result = await self.db.execute(
            select(AnalysisResult.improvements)
            .where(AnalysisResult.improvements.isnot(None))
            .limit(500)
        )
        rows = result.scalars().all()

        counter: Counter[str] = Counter()
        section_keywords = {
            "Summary": ["summary", "objective", "professional summary"],
            "Skills": ["skills", "technical skills"],
            "Projects": ["project"],
            "Experience": ["experience", "work experience"],
            "Education": ["education"],
            "Formatting": ["format", "header", "ats"],
        }

        for improvements in rows:
            if not isinstance(improvements, list):
                continue
            for imp in improvements:
                imp_lower = imp.lower() if isinstance(imp, str) else ""
                for section, keywords in section_keywords.items():
                    if any(kw in imp_lower for kw in keywords):
                        counter[section] += 1
                        break

        return [
            {"section": section, "count": count}
            for section, count in counter.most_common(10)
        ]
