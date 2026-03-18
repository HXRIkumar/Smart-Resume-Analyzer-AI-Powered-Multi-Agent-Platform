"""Pydantic v2 schemas for Resume upload and response."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ─── Response Schemas ────────────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    """Full resume representation returned from API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    file_path: str
    file_size_bytes: int
    uploaded_at: datetime


class ResumeUploadResponse(BaseModel):
    """Response after successful resume upload."""

    id: uuid.UUID
    original_filename: str
    file_size_bytes: int
    message: str = "Resume uploaded successfully"
