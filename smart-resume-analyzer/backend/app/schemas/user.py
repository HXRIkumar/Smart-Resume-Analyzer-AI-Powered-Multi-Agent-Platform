"""Pydantic v2 schemas for User operations."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ─── Request Schemas ─────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Schema for email/password login."""

    email: EmailStr
    password: str = Field(min_length=1)


class UserUpdate(BaseModel):
    """Schema for updating user profile (partial update)."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None


# ─── Response Schemas ────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """Public user representation — never exposes password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
