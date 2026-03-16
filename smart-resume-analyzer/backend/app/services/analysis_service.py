"""Analysis service — orchestrates the AI pipeline."""

import json
import time

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import AnalysisResult
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.agents.pipeline import AgentPipeline
from app.schemas.analysis import AnalysisSummary
from app.utils.exceptions import NotFoundError


class AnalysisService:
    """Orchestrates resume analysis via the multi-agent AI pipeline."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_analysis(
        self, resume_id: int, user_id: int, job_description_id: int | None = None
    ) -> AnalysisResult:
        """Create a pending analysis record."""
        # Verify resume belongs to user
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise NotFoundError("Resume not found")

        analysis = AnalysisResult(
            resume_id=resume_id,
            job_description_id=job_description_id,
            status="pending",
        )
        self.db.add(analysis)
        await self.db.flush()
        await self.db.refresh(analysis)
        return analysis

    async def run_pipeline(self, analysis_id: int) -> None:
        """Execute the full AI agent pipeline (runs in background)."""
        result = await self.db.execute(
            select(AnalysisResult).where(AnalysisResult.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()
        if not analysis:
            return

        # Load resume text
        resume_result = await self.db.execute(
            select(Resume).where(Resume.id == analysis.resume_id)
        )
        resume = resume_result.scalar_one_or_none()
        if not resume:
            return

        # Load job description if present
        jd_text = None
        if analysis.job_description_id:
            jd_result = await self.db.execute(
                select(JobDescription).where(JobDescription.id == analysis.job_description_id)
            )
            jd = jd_result.scalar_one_or_none()
            jd_text = jd.description if jd else None

        try:
            analysis.status = "processing"
            await self.db.flush()

            start = time.time()
            pipeline = AgentPipeline()
            result_data = await pipeline.execute(
                resume_path=resume.file_path,
                resume_text=resume.raw_text,
                job_description=jd_text,
            )
            elapsed_ms = int((time.time() - start) * 1000)

            # Update analysis with results
            analysis.overall_score = result_data.get("overall_score", 0.0)
            analysis.ats_score = result_data.get("ats_score", 0.0)
            analysis.skill_match_score = result_data.get("skill_match_score", 0.0)
            analysis.extracted_skills = json.dumps(result_data.get("extracted_skills", []))
            analysis.skill_gaps = json.dumps(result_data.get("skill_gaps", []))
            analysis.feedback = result_data.get("feedback", "")
            analysis.career_predictions = json.dumps(result_data.get("career_predictions", []))
            analysis.ats_issues = json.dumps(result_data.get("ats_issues", []))
            analysis.processing_time_ms = elapsed_ms
            analysis.status = "completed"
        except Exception as e:
            analysis.status = "failed"
            analysis.feedback = f"Pipeline error: {str(e)}"

        await self.db.flush()

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[AnalysisResult], int]:
        """List analyses for a user (via resume ownership)."""
        query = (
            select(AnalysisResult)
            .join(Resume, AnalysisResult.resume_id == Resume.id)
            .where(Resume.user_id == user_id)
            .order_by(AnalysisResult.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        analyses = list(result.scalars().all())

        count_result = await self.db.execute(
            select(func.count(AnalysisResult.id))
            .join(Resume, AnalysisResult.resume_id == Resume.id)
            .where(Resume.user_id == user_id)
        )
        total = count_result.scalar() or 0
        return analyses, total

    async def get_by_id(self, analysis_id: int, user_id: int) -> AnalysisResult | None:
        """Get a specific analysis, scoped to user's resumes."""
        result = await self.db.execute(
            select(AnalysisResult)
            .join(Resume, AnalysisResult.resume_id == Resume.id)
            .where(AnalysisResult.id == analysis_id, Resume.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_summary(self, user_id: int) -> AnalysisSummary:
        """Get aggregated analysis stats for the dashboard."""
        # Total analyses
        count_result = await self.db.execute(
            select(func.count(AnalysisResult.id))
            .join(Resume, AnalysisResult.resume_id == Resume.id)
            .where(Resume.user_id == user_id, AnalysisResult.status == "completed")
        )
        total = count_result.scalar() or 0

        # Average score
        avg_result = await self.db.execute(
            select(func.avg(AnalysisResult.overall_score))
            .join(Resume, AnalysisResult.resume_id == Resume.id)
            .where(Resume.user_id == user_id, AnalysisResult.status == "completed")
        )
        avg_score = round(float(avg_result.scalar() or 0), 1)

        return AnalysisSummary(
            total_analyses=total,
            average_score=avg_score,
            top_skills=[],
            improvement_areas=[],
        )
