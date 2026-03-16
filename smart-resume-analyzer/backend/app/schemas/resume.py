"""Pydantic schemas for Resume."""

from datetime import datetime

from pydantic import BaseModel


class ResumeBase(BaseModel):
    filename: str


class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    file_size_bytes: int
    mime_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeListResponse(BaseModel):
    resumes: list[ResumeResponse]
    total: int


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    message: str = "Resume uploaded successfully"
