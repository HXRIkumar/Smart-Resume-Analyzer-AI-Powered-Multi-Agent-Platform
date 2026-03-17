"""001 — Initial schema: users, resumes, job_descriptions, analysis_results.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all application tables."""

    # ── users ────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("role", sa.String(10), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("google_id", sa.String(255), unique=True, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── resumes ──────────────────────────────────────────────────────────
    op.create_table(
        "resumes",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    # ── job_descriptions ─────────────────────────────────────────────────
    op.create_table(
        "job_descriptions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description_text", sa.Text(), nullable=False),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── analysis_results ─────────────────────────────────────────────────
    op.create_table(
        "analysis_results",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("resume_id", pg.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("job_id", pg.UUID(as_uuid=True), sa.ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True),
        # Overall scores
        sa.Column("resume_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ats_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ai_confidence", sa.Float(), nullable=False, server_default="0.0"),
        # Category scores
        sa.Column("objectives_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skills_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("projects_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("formatting_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("experience_score", sa.Integer(), nullable=False, server_default="0"),
        # Skills (PostgreSQL ARRAY)
        sa.Column("present_skills", pg.ARRAY(sa.String()), nullable=True),
        sa.Column("missing_skills", pg.ARRAY(sa.String()), nullable=True),
        # JSON payloads
        sa.Column("recommended_skills", pg.JSON(), nullable=True),
        sa.Column("recommended_courses", pg.JSON(), nullable=True),
        sa.Column("career_predictions", pg.JSON(), nullable=True),
        sa.Column("keyword_heatmap", pg.JSON(), nullable=True),
        # Strengths / Improvements (PostgreSQL ARRAY)
        sa.Column("strengths", pg.ARRAY(sa.String()), nullable=True),
        sa.Column("improvements", pg.ARRAY(sa.String()), nullable=True),
        # AI feedback
        sa.Column("ai_feedback_text", sa.Text(), nullable=True),
        # Audit trail
        sa.Column("agent_pipeline_log", pg.JSON(), nullable=True),
        # Timestamp
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_analysis_results_resume_id", "analysis_results", ["resume_id"])


def downgrade() -> None:
    """Drop all application tables in reverse dependency order."""
    op.drop_table("analysis_results")
    op.drop_table("job_descriptions")
    op.drop_table("resumes")
    op.drop_table("users")
