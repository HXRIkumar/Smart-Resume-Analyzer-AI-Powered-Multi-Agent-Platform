"""Custom HTTP exceptions for the Smart Resume Analyzer.

Provides domain-specific exception classes with appropriate HTTP status
codes, enabling clean error handling throughout routers and services.
"""

from typing import Any

from fastapi import HTTPException, status


# ─── Base Exceptions (pre-existing) ─────────────────────────────────────────

class NotFoundError(HTTPException):
    """Generic 404 — resource not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPException):
    """409 — resource already exists."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class BadRequestError(HTTPException):
    """400 — malformed or invalid request."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedError(HTTPException):
    """401 — authentication required or failed."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(HTTPException):
    """403 — insufficient permissions."""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# ─── Domain-Specific Exceptions ─────────────────────────────────────────────

class ResumeNotFoundError(HTTPException):
    """404 — the requested resume does not exist."""

    def __init__(self, resume_id: Any = None):
        detail = f"Resume not found: {resume_id}" if resume_id else "Resume not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AnalysisNotFoundError(HTTPException):
    """404 — the requested analysis result does not exist."""

    def __init__(self, analysis_id: Any = None):
        detail = f"Analysis not found: {analysis_id}" if analysis_id else "Analysis not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedResumeAccess(HTTPException):
    """403 — user does not own this resume."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resume",
        )


class InvalidFileTypeError(HTTPException):
    """400 — uploaded file is not a PDF."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted. Please upload a .pdf file.",
        )


class FileTooLargeError(HTTPException):
    """413 — uploaded file exceeds the size limit."""

    def __init__(self, max_mb: int = 10):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the {max_mb}MB limit",
        )


class DuplicateEmailError(HTTPException):
    """409 — email address already registered."""

    def __init__(self, email: str | None = None):
        detail = f"Email already registered: {email}" if email else "Email already registered"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class AgentPipelineError(HTTPException):
    """500 — the AI agent pipeline encountered an unrecoverable error."""

    def __init__(self, agent_name: str = "unknown", error: str = ""):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "AI analysis pipeline failed",
                "agent": agent_name,
                "error": error,
            },
        )
