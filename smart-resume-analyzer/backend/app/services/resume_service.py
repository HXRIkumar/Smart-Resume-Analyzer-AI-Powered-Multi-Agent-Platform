"""Resume service — CRUD + file handling."""

import os
import uuid

from fastapi import UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.resume import Resume
from app.utils.exceptions import BadRequestError, NotFoundError
from app.utils.file_utils import save_upload_file, delete_file


class ResumeService:
    """Handles resume CRUD operations and file management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload(self, file: UploadFile, user_id: int) -> Resume:
        """Save uploaded PDF and create database record."""
        # Validate file size
        content = await file.read()
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise BadRequestError(f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit")

        # Save to disk
        ext = os.path.splitext(file.filename or "resume.pdf")[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = save_upload_file(content, unique_name)

        resume = Resume(
            user_id=user_id,
            filename=file.filename or "resume.pdf",
            file_path=file_path,
            file_size_bytes=len(content),
            mime_type=file.content_type or "application/pdf",
        )
        self.db.add(resume)
        await self.db.flush()
        await self.db.refresh(resume)
        return resume

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Resume], int]:
        """List resumes for a user with pagination."""
        query = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        resumes = list(result.scalars().all())

        count_result = await self.db.execute(
            select(func.count(Resume.id)).where(Resume.user_id == user_id)
        )
        total = count_result.scalar() or 0
        return resumes, total

    async def get_by_id(self, resume_id: int, user_id: int) -> Resume | None:
        """Get a specific resume by ID, scoped to user."""
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, resume_id: int, user_id: int) -> bool:
        """Delete a resume and its file from disk."""
        resume = await self.get_by_id(resume_id, user_id)
        if not resume:
            return False
        delete_file(resume.file_path)
        await self.db.delete(resume)
        return True
