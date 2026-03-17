"""Resume ORM model — uploaded resume metadata and extracted text."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Resume(Base):
    """An uploaded resume PDF with parsed text content.

    Belongs to a User (many-to-one).
    Has many AnalysisResult records (one-to-many).
    """

    __tablename__ = "resumes"

    # ─── Primary Key ─────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ─── Owner ───────────────────────────────────────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # ─── File Metadata ───────────────────────────────────────────────────
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # ─── Extracted Content ───────────────────────────────────────────────
    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,  # populated after ParserAgent runs
    )

    # ─── Timestamps ──────────────────────────────────────────────────────
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ─── Relationships ───────────────────────────────────────────────────
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="resumes",
        lazy="selectin",
    )
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(  # noqa: F821
        "AnalysisResult",
        back_populates="resume",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Resume id={self.id!s} "
            f"filename={self.original_filename!r} "
            f"size={self.file_size_bytes}>"
        )
