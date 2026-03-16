"""Models package — import all models so Alembic can detect them."""

from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.analysis import AnalysisResult

__all__ = ["User", "Resume", "JobDescription", "AnalysisResult"]
