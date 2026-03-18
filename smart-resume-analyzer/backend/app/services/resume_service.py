"""Resume service — file upload, CRUD, and ownership checks."""

import os
import uuid as uuid_mod
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.resume import Resume
from app.utils.exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    ResumeNotFoundError,
    UnauthorizedResumeAccess,
)


class ResumeService:
    """Handles resume file upload, retrieval, and deletion.

    All queries are scoped to the authenticated user's ID to
    enforce ownership — a user can only access their own resumes.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_resume(
        self, user_id: UUID, file: UploadFile
    ) -> Resume:
        """Validate, save, and record a resume PDF upload.

        Args:
            user_id: Authenticated user's UUID.
            file: FastAPI UploadFile from the request.

        Returns:
            The created Resume ORM instance.

        Raises:
            InvalidFileTypeError: If file is not a PDF.
            FileTooLargeError: If file exceeds MAX_FILE_SIZE_MB.
        """
        # ── Validate file type ───────────────────────────────────────────
        content_type = file.content_type or ""
        filename = file.filename or "resume.pdf"

        if content_type != "application/pdf" and not filename.lower().endswith(".pdf"):
            raise InvalidFileTypeError()

        # ── Read and validate size ───────────────────────────────────────
        content = await file.read()
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise FileTooLargeError(max_mb=settings.MAX_FILE_SIZE_MB)

        # ── Generate unique filename and save ────────────────────────────
        safe_original = filename.replace(" ", "_")
        unique_name = f"{uuid_mod.uuid4().hex}_{safe_original}"
        user_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        file_path = os.path.join(user_dir, unique_name)
        with open(file_path, "wb") as f:
            f.write(content)

        # ── Create DB record ────────────────────────────────────────────
        resume = Resume(
            user_id=user_id,
            original_filename=filename,
            file_path=file_path,
            file_size_bytes=len(content),
        )
        self.db.add(resume)
        await self.db.flush()
        await self.db.refresh(resume)
        return resume

    async def get_user_resumes(self, user_id: UUID) -> list[Resume]:
        """Return all resumes belonging to a user, newest first.

        Args:
            user_id: Owner's UUID.

        Returns:
            List of Resume models.
        """
        result = await self.db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.uploaded_at.desc())
        )
        return list(result.scalars().all())

    async def get_resume_by_id(
        self, resume_id: UUID, user_id: UUID
    ) -> Resume:
        """Fetch a single resume, enforcing ownership.

        Args:
            resume_id: Target resume UUID.
            user_id: Authenticated user's UUID.

        Returns:
            Resume model.

        Raises:
            ResumeNotFoundError: If resume does not exist.
            UnauthorizedResumeAccess: If user does not own the resume.
        """
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id)
        )
        resume = result.scalar_one_or_none()
        if resume is None:
            raise ResumeNotFoundError(resume_id)
        if resume.user_id != user_id:
            raise UnauthorizedResumeAccess()
        return resume

    async def delete_resume(
        self, resume_id: UUID, user_id: UUID
    ) -> bool:
        """Delete a resume record and its file from disk.

        Args:
            resume_id: Target resume UUID.
            user_id: Authenticated user's UUID.

        Returns:
            True if deleted successfully.

        Raises:
            ResumeNotFoundError: If resume does not exist.
            UnauthorizedResumeAccess: If user does not own the resume.
        """
        resume = await self.get_resume_by_id(resume_id, user_id)

        # Remove file from disk
        try:
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
        except OSError:
            pass  # File already deleted or inaccessible

        await self.db.delete(resume)
        return True
