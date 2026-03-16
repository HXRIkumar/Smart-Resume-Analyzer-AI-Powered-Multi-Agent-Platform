"""Job router — /job/* endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.job_description import JobDescription

router = APIRouter()


# ─── Inline schemas ───
class JobDescriptionCreate(BaseModel):
    title: str
    company: str | None = None
    description: str
    required_skills: str | None = None
    experience_level: str | None = None


class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    company: str | None
    description: str
    required_skills: str | None
    experience_level: str | None

    model_config = {"from_attributes": True}


class JobDescriptionListResponse(BaseModel):
    jobs: list[JobDescriptionResponse]
    total: int


# ─── Endpoints ───
@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    data: JobDescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job description."""
    job = JobDescription(
        user_id=current_user.id,
        title=data.title,
        company=data.company,
        description=data.description,
        required_skills=data.required_skills,
        experience_level=data.experience_level,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


@router.get("/", response_model=JobDescriptionListResponse)
async def list_job_descriptions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all job descriptions for the current user."""
    query = (
        select(JobDescription)
        .where(JobDescription.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(JobDescription.created_at.desc())
    )
    result = await db.execute(query)
    jobs = result.scalars().all()

    count_result = await db.execute(
        select(JobDescription.id).where(JobDescription.user_id == current_user.id)
    )
    total = len(count_result.all())
    return JobDescriptionListResponse(jobs=jobs, total=total)


@router.get("/{job_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific job description."""
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_description(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a job description."""
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    await db.delete(job)
