"""Job description router — /job/* endpoints for CRUD operations."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.job_description import JobDescription
from app.models.user import User
from app.schemas.analysis import JobDescriptionCreate, JobDescriptionResponse
from app.utils.exceptions import NotFoundError

router = APIRouter()


@router.post(
    "/submit",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a job description",
    description=(
        "Create a new job description entry. The description text "
        "is used for skill gap analysis during resume evaluation."
    ),
)
async def submit_job_description(
    data: JobDescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit a new job description for matching."""
    job = JobDescription(
        user_id=current_user.id,
        title=data.title,
        description_text=data.description_text,
        company=data.company,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


@router.get(
    "/",
    response_model=list[JobDescriptionResponse],
    summary="List user's job descriptions",
    description="Returns all job descriptions created by the authenticated user, newest first.",
)
async def list_job_descriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all job descriptions for the current user."""
    result = await db.execute(
        select(JobDescription)
        .where(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
    )
    return list(result.scalars().all())


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job description",
    description="Delete a job description by ID. Returns 404 if not found or not owned.",
)
async def delete_job_description(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a job description by ID."""
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundError("Job description not found")
    await db.delete(job)
