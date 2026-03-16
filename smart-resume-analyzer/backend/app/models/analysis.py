"""AnalysisResult SQLAlchemy model."""

import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    job_description_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("job_descriptions.id"), nullable=True
    )

    # Scores
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ats_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    skill_match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Agent outputs (JSON strings)
    extracted_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    skill_gaps: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_predictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    ats_issues: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending | processing | completed | failed
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    resume = relationship("Resume", back_populates="analyses")

    def __repr__(self) -> str:
        return f"<AnalysisResult(id={self.id}, score={self.overall_score})>"
