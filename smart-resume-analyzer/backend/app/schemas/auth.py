"""Pydantic v2 schemas for authentication flows."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


# ─── Token Response ──────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """JWT token returned after successful authentication."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Google OAuth ────────────────────────────────────────────────────────────

class GoogleAuthRequest(BaseModel):
    """Payload for Google OAuth code exchange."""

    code: str = Field(min_length=1, description="Authorization code from Google")
    redirect_uri: str = Field(min_length=1, description="OAuth redirect URI")


# ─── Password Reset ─────────────────────────────────────────────────────────

class PasswordResetRequest(BaseModel):
    """Payload for initiating a password reset."""

    email: EmailStr
