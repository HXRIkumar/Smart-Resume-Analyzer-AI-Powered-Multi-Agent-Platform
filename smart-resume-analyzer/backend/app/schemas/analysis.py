"""Pydantic v2 schemas for analysis request/response."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ─── Request Schemas ─────────────────────────────────────────────────────────

class AnalysisCreate(BaseModel):
    """Payload to trigger a new resume analysis."""

    resume_id: uuid.UUID
    job_id: uuid.UUID | None = Field(
        default=None,
        description="Optional job description ID for targeted matching",
    )


# ─── Response Schemas ────────────────────────────────────────────────────────

class AnalysisSummary(BaseModel):
    """Lightweight summary for list views and cards."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_score: int
    ats_score: int
    created_at: datetime


class AnalysisResponse(BaseModel):
    """Full analysis result with all scores, skills, and feedback."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID | None = None

    # ─── Scores ──────────────────────────────────────────────────────────
    resume_score: int = 0
    ats_score: int = 0
    ai_confidence: float = 0.0
    objectives_score: int = 0
    skills_score: int = 0
    projects_score: int = 0
    formatting_score: int = 0
    experience_score: int = 0

    # ─── Skills ──────────────────────────────────────────────────────────
    present_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommended_skills: dict | None = None

    # ─── Recommendations ─────────────────────────────────────────────────
    recommended_courses: dict | None = None
    career_predictions: dict | None = None
    keyword_heatmap: dict | None = None

    # ─── Feedback ────────────────────────────────────────────────────────
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    ai_feedback_text: str | None = None

    # ─── Audit ───────────────────────────────────────────────────────────
    agent_pipeline_log: dict | None = None

    # ─── Timestamp ───────────────────────────────────────────────────────
    created_at: datetime
