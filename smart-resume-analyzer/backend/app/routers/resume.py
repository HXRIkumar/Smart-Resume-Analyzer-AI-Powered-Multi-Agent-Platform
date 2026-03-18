"""Resume router — /resume/* endpoints for upload, list, get, delete."""

import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.resume import ResumeResponse, ResumeUploadResponse
from app.services.resume_service import ResumeService

router = APIRouter()


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a resume PDF",
    description=(
        "Upload a single PDF file (max 10MB). "
        "The file is saved to the server and a database record is created."
    ),
)
async def upload_resume(
    file: UploadFile = File(
        ..., description="PDF resume file to upload"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a new resume PDF file."""
    service = ResumeService(db)
    resume = await service.upload_resume(
        user_id=current_user.id, file=file
    )
    return ResumeUploadResponse(
        id=resume.id,
        original_filename=resume.original_filename,
        file_size_bytes=resume.file_size_bytes,
    )


@router.get(
    "/",
    response_model=list[ResumeResponse],
    summary="List user's resumes",
    description="Returns all resumes uploaded by the authenticated user, newest first.",
)
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all resumes for the current user."""
    service = ResumeService(db)
    return await service.get_user_resumes(user_id=current_user.id)


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Get a specific resume",
    description="Fetch a single resume by ID. Returns 403 if the user does not own it.",
)
async def get_resume(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific resume by ID."""
    service = ResumeService(db)
    return await service.get_resume_by_id(
        resume_id=resume_id, user_id=current_user.id
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resume",
    description="Delete a resume and its PDF file from disk. Returns 404 if not found.",
)
async def delete_resume(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a resume by ID."""
    service = ResumeService(db)
    await service.delete_resume(
        resume_id=resume_id, user_id=current_user.id
    )
