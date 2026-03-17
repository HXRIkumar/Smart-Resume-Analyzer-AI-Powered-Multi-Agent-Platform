"""AnalysisResult ORM model — comprehensive resume analysis output.

Stores scores, extracted skills, AI feedback, career predictions,
and the full agent pipeline audit trail.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AnalysisResult(Base):
    """Result of running the multi-agent AI pipeline on a resume.

    Contains granular scores, skill arrays, AI-generated feedback,
    career predictions, and a full agent audit log.
    """

    __tablename__ = "analysis_results"

    # ─── Primary Key ─────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ─── Foreign Keys ────────────────────────────────────────────────────
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ─── Overall Scores ──────────────────────────────────────────────────
    resume_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Overall resume score (0-100)",
    )
    ats_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="ATS compatibility score (0-100)",
    )
    ai_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="AI model confidence (0.0-1.0)",
    )

    # ─── Category Scores ─────────────────────────────────────────────────
    objectives_score: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
    )
    skills_score: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
    )
    projects_score: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
    )
    formatting_score: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
    )
    experience_score: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
    )

    # ─── Skills (PostgreSQL ARRAY) ───────────────────────────────────────
    present_skills: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=list,
    )
    missing_skills: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=list,
    )

    # ─── JSON Payloads ───────────────────────────────────────────────────
    recommended_skills: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment='e.g. {"technical": [...], "soft": [...]}',
    )
    recommended_courses: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment='e.g. [{"title": "...", "url": "...", "platform": "..."}]',
    )
    career_predictions: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment='e.g. [{"role": "...", "confidence": 0.9, "rank": 1}]',
    )
    keyword_heatmap: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment='e.g. [{"keyword": "...", "impact": 0.8, "frequency": 3}]',
    )

    # ─── Strengths & Improvements (PostgreSQL ARRAY) ─────────────────────
    strengths: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=list,
    )
    improvements: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=list,
    )

    # ─── AI Feedback ─────────────────────────────────────────────────────
    ai_feedback_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Full-text AI-generated feedback and suggestions",
    )

    # ─── Audit Trail ─────────────────────────────────────────────────────
    agent_pipeline_log: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment="Execution log for each agent in the pipeline",
    )

    # ─── Timestamps ──────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ─── Relationships ───────────────────────────────────────────────────
    resume: Mapped["Resume"] = relationship(  # noqa: F821
        "Resume",
        back_populates="analysis_results",
        lazy="selectin",
    )
    job_description: Mapped["JobDescription | None"] = relationship(  # noqa: F821
        "JobDescription",
        back_populates="analysis_results",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<AnalysisResult id={self.id!s} "
            f"resume_score={self.resume_score} "
            f"ats_score={self.ats_score}>"
        )
