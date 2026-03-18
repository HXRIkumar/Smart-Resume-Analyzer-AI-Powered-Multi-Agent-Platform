"""Pydantic schemas — re-export all schemas for clean imports."""

from app.schemas.user import (  # noqa: F401
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.schemas.auth import (  # noqa: F401
    TokenResponse,
    GoogleAuthRequest,
    PasswordResetRequest,
)
from app.schemas.analysis import (  # noqa: F401
    AdminAnalyticsResponse,
    AnalysisCreate,
    AnalysisResponse,
    AnalysisSummary,
    JobDescriptionCreate,
    JobDescriptionResponse,
    MonthlyCount,
)
from app.schemas.resume import (  # noqa: F401
    ResumeResponse,
    ResumeUploadResponse,
)

__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    # Auth
    "TokenResponse",
    "GoogleAuthRequest",
    "PasswordResetRequest",
    # Analysis
    "AdminAnalyticsResponse",
    "AnalysisCreate",
    "AnalysisResponse",
    "AnalysisSummary",
    "MonthlyCount",
    # Job
    "JobDescriptionCreate",
    "JobDescriptionResponse",
    # Resume
    "ResumeResponse",
    "ResumeUploadResponse",
]
