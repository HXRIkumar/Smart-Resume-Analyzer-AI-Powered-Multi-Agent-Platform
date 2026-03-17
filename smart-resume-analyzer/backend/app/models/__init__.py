"""ORM models — import all models so Alembic autogenerate detects them."""

from app.models.user import User, UserRole  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.job_description import JobDescription  # noqa: F401
from app.models.analysis import AnalysisResult  # noqa: F401

__all__ = [
    "User",
    "UserRole",
    "Resume",
    "JobDescription",
    "AnalysisResult",
]
