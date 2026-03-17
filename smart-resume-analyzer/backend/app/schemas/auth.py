"""Pydantic v2 schemas for authentication flows."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


# ─── Token Response ──────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """JWT tokens returned after successful authentication."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user: UserResponse


# ─── Google OAuth ────────────────────────────────────────────────────────────

class GoogleAuthRequest(BaseModel):
    """Payload for Google OAuth authorization code exchange."""

    code: str = Field(min_length=1, description="Authorization code from Google")
    redirect_uri: str = Field(min_length=1, description="OAuth redirect URI")


# ─── Refresh Token ───────────────────────────────────────────────────────────

class RefreshTokenRequest(BaseModel):
    """Payload for refreshing an access token."""

    refresh_token: str = Field(min_length=1, description="JWT refresh token")


# ─── Password Reset ─────────────────────────────────────────────────────────

class PasswordResetRequest(BaseModel):
    """Payload for initiating a password reset."""

    email: EmailStr
