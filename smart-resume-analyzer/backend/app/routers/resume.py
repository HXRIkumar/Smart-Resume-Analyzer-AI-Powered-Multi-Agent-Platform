"""Resume router — /resume/* endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeListResponse, ResumeResponse, ResumeUploadResponse
from app.services.resume_service import ResumeService

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a resume PDF."""
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted",
        )
    service = ResumeService(db)
    resume = await service.upload(file=file, user_id=current_user.id)
    return ResumeUploadResponse(id=resume.id, filename=resume.filename)


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all resumes for the current user."""
    service = ResumeService(db)
    resumes, total = await service.list_by_user(user_id=current_user.id, skip=skip, limit=limit)
    return ResumeListResponse(resumes=resumes, total=total)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific resume."""
    service = ResumeService(db)
    resume = await service.get_by_id(resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resume."""
    service = ResumeService(db)
    deleted = await service.delete(resume_id=resume_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
