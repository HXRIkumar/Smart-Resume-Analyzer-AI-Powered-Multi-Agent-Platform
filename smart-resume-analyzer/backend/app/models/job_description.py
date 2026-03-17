"""Job Description ORM model — target roles for resume matching."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobDescription(Base):
    """A job posting used to evaluate resume–job fit.

    Belongs to a User. Optionally linked to AnalysisResult records.
    """

    __tablename__ = "job_descriptions"

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

    # ─── Content ─────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ─── Timestamps ──────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ─── Relationships ───────────────────────────────────────────────────
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        lazy="selectin",
    )
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(  # noqa: F821
        "AnalysisResult",
        back_populates="job_description",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<JobDescription id={self.id!s} "
            f"title={self.title!r} "
            f"company={self.company!r}>"
        )
