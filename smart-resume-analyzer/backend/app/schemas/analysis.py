"""Pydantic schemas for Analysis."""

from datetime import datetime

from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    resume_id: int
    job_description_id: int | None = None


class SkillDetail(BaseModel):
    name: str
    category: str
    proficiency: str | None = None


class ATSIssue(BaseModel):
    issue: str
    severity: str  # low | medium | high
    suggestion: str


class CareerPrediction(BaseModel):
    role: str
    confidence: float
    reasoning: str


class AnalysisResponse(BaseModel):
    id: int
    resume_id: int
    overall_score: float
    ats_score: float
    skill_match_score: float
    extracted_skills: list[SkillDetail] | None = None
    skill_gaps: list[str] | None = None
    feedback: str | None = None
    career_predictions: list[CareerPrediction] | None = None
    ats_issues: list[ATSIssue] | None = None
    status: str
    processing_time_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListResponse(BaseModel):
    analyses: list[AnalysisResponse]
    total: int


class AnalysisSummary(BaseModel):
    total_analyses: int
    average_score: float
    top_skills: list[str]
    improvement_areas: list[str]
