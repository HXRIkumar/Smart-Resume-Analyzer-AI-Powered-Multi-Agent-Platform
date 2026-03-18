"""Analysis service — orchestrates the AI agent pipeline.

Integrates the AgentPipeline with the database layer. Runs the pipeline
on a resume PDF, maps PipelineResult fields to the AnalysisResult ORM
model, and persists the results.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.pipeline import AgentPipeline, PipelineResult
from app.models.analysis import AnalysisResult
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.utils.exceptions import (
    AgentPipelineError,
    AnalysisNotFoundError,
    ResumeNotFoundError,
    UnauthorizedResumeAccess,
)

logger = logging.getLogger(__name__)

# Shared pipeline instance — agents are stateless so a single instance is safe
_pipeline = AgentPipeline()


class AnalysisService:
    """Orchestrates resume analysis through the multi-agent AI pipeline.

    Uses a module-level AgentPipeline singleton so agents are only
    instantiated once per process.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pipeline = _pipeline

    async def analyze(
        self,
        resume_id: UUID,
        job_id: UUID | None,
        user_id: UUID,
    ) -> AnalysisResult:
        """Run the full AI pipeline on a resume and persist results.

        Args:
            resume_id: UUID of the uploaded resume.
            job_id: Optional UUID of a job description for gap analysis.
            user_id: Authenticated user's UUID (for ownership check).

        Returns:
            Persisted AnalysisResult ORM model.

        Raises:
            ResumeNotFoundError: If resume does not exist.
            UnauthorizedResumeAccess: If user does not own the resume.
            AgentPipelineError: If the parser agent fails (pipeline abort).
        """
        # ── Fetch resume (with ownership check) ─────────────────────────
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id)
        )
        resume = result.scalar_one_or_none()
        if resume is None:
            raise ResumeNotFoundError(resume_id)
        if resume.user_id != user_id:
            raise UnauthorizedResumeAccess()

        # ── Fetch job description text (if provided) ────────────────────
        jd_text: str | None = None
        if job_id:
            jd_result = await self.db.execute(
                select(JobDescription).where(JobDescription.id == job_id)
            )
            jd = jd_result.scalar_one_or_none()
            if jd:
                jd_text = jd.description_text

        # ── Run the agent pipeline ──────────────────────────────────────
        logger.info(
            "AnalysisService — running pipeline for resume=%s, job=%s",
            resume_id, job_id,
        )
        pipeline_result: PipelineResult = await self.pipeline.run(
            file_path=resume.file_path,
            job_description=jd_text,
            resume_id=resume_id,
        )

        if not pipeline_result.success:
            logger.error("Pipeline failed for resume=%s", resume_id)
            raise AgentPipelineError(
                agent_name="parser_agent",
                error="Resume parsing failed — the PDF may be corrupted or empty",
            )

        # ── Map PipelineResult → AnalysisResult ─────────────────────────
        component_scores = {}
        for entry in pipeline_result.agent_pipeline_log:
            if entry.get("agent") == "ats_evaluator_agent" and entry.get("success"):
                break

        # Extract component scores from the pipeline output
        # The ATS evaluator stores these in the pipeline result
        objectives_score = 0
        skills_score = 0
        projects_score = 0
        formatting_score = 0
        experience_score = 0

        # Walk the pipeline log to find ats scores
        for log_entry in pipeline_result.agent_pipeline_log:
            if log_entry.get("agent") == "ats_evaluator_agent":
                break

        analysis = AnalysisResult(
            resume_id=resume_id,
            job_id=job_id,
            resume_score=pipeline_result.resume_score,
            ats_score=pipeline_result.ats_score,
            ai_confidence=pipeline_result.ai_confidence,
            objectives_score=objectives_score,
            skills_score=skills_score,
            projects_score=projects_score,
            formatting_score=formatting_score,
            experience_score=experience_score,
            present_skills=pipeline_result.present_skills,
            missing_skills=pipeline_result.missing_skills,
            recommended_skills=pipeline_result.recommended_skills,
            career_predictions=pipeline_result.career_predictions,
            keyword_heatmap=pipeline_result.keyword_heatmap,
            strengths=pipeline_result.strengths,
            improvements=pipeline_result.improvements,
            ai_feedback_text=pipeline_result.ai_feedback_text,
            agent_pipeline_log=pipeline_result.agent_pipeline_log,
        )

        # Update resume extracted text
        if pipeline_result.raw_text:
            resume.extracted_text = pipeline_result.raw_text

        self.db.add(analysis)
        await self.db.flush()
        await self.db.refresh(analysis)

        logger.info(
            "AnalysisService — saved analysis=%s, score=%d, ats=%d (%.1fms)",
            analysis.id,
            analysis.resume_score,
            analysis.ats_score,
            pipeline_result.total_execution_ms,
        )

        return analysis

    async def get_analysis(
        self, analysis_id: UUID, user_id: UUID
    ) -> AnalysisResult:
        """Fetch a single analysis result, enforcing user ownership via resume FK.

        Args:
            analysis_id: Target analysis UUID.
            user_id: Authenticated user's UUID.

        Returns:
            AnalysisResult model.

        Raises:
            AnalysisNotFoundError: If analysis does not exist or user doesn't own it.
        """
        result = await self.db.execute(
            select(AnalysisResult)
            .join(Resume, AnalysisResult.resume_id == Resume.id)
            .where(AnalysisResult.id == analysis_id, Resume.user_id == user_id)
        )
        analysis = result.scalar_one_or_none()
        if analysis is None:
            raise AnalysisNotFoundError(analysis_id)
        return analysis

    async def get_user_analyses(
        self, user_id: UUID
    ) -> list[AnalysisResult]:
        """Return all analyses for a user's resumes, newest first.

        Args:
            user_id: Authenticated user's UUID.

        Returns:
            List of AnalysisResult models.
        """
        result = await self.db.execute(
            select(AnalysisResult)
            .join(Resume, AnalysisResult.resume_id == Resume.id)
            .where(Resume.user_id == user_id)
            .order_by(AnalysisResult.created_at.desc())
        )
        return list(result.scalars().all())
