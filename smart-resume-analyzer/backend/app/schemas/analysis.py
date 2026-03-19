"""Pydantic v2 schemas for analysis request/response."""

import uuid
from datetime import datetime
from typing import Any

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
    resume_id: uuid.UUID
    resume_score: int
    ats_score: int
    ai_confidence: float = 0.0
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
    recommended_skills: list | dict | None = None

    # ─── Recommendations ─────────────────────────────────────────────────
    recommended_courses: dict | None = None
    career_predictions: dict | None = None
    keyword_heatmap: dict | None = None

    # ─── Feedback ────────────────────────────────────────────────────────
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    ai_feedback_text: str | None = None

    # ─── Audit ───────────────────────────────────────────────────────────
    agent_pipeline_log: list | dict | None = None

    # ─── Timestamp ───────────────────────────────────────────────────────
    created_at: datetime


# ─── Job Description Schemas ─────────────────────────────────────────────────

class JobDescriptionCreate(BaseModel):
    """Payload to create a new job description."""

    title: str = Field(min_length=1, max_length=255)
    description_text: str = Field(min_length=1)
    company: str | None = Field(default=None, max_length=255)


class JobDescriptionResponse(BaseModel):
    """Job description returned from API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description_text: str
    company: str | None = None
    created_at: datetime


# ─── Admin Analytics Schemas ─────────────────────────────────────────────────

class MonthlyCount(BaseModel):
    """Single month data point for time-series chart."""

    month: str  # e.g. "2026-03"
    count: int


class AdminAnalyticsResponse(BaseModel):
    """Platform-wide analytics returned to admin dashboard."""

    total_users: int = 0
    total_resumes: int = 0
    total_applications: int = 0
    avg_resume_score: float = 0.0
    most_popular_career: str = ""
    applications_over_time: list[MonthlyCount] = Field(default_factory=list)
    score_distribution: dict[str, int] = Field(
        default_factory=lambda: {
            "0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0,
        },
        description="Histogram buckets for resume scores",
    )
    top_missing_sections: list[dict[str, Any]] = Field(default_factory=list)
    conversion_rate: float = 30.0
