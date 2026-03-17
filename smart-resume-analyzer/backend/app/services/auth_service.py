"""Authentication service — registration, login, Google OAuth, token refresh.

All business logic for user authentication flows. Uses the security
module for password hashing and token management. Database operations
use async SQLAlchemy sessions.
"""

from datetime import timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.utils.exceptions import ConflictError, UnauthorizedError
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

# Google OAuth endpoints
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class AuthService:
    """Handles user registration, authentication, and JWT lifecycle.

    All methods are async and operate on the provided database session.
    The caller is responsible for committing the transaction.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the auth service with a database session.

        Args:
            db: Async SQLAlchemy session.
        """
        self.db = db

    # ─── Registration ────────────────────────────────────────────────────

    async def register(self, user_create: UserCreate) -> User:
        """Register a new user with email/password.

        Args:
            user_create: Validated registration payload (email, password, full_name).

        Returns:
            The newly created User model instance.

        Raises:
            ConflictError (409): If the email is already registered.
        """
        # Check email uniqueness
        result = await self.db.execute(
            select(User).where(User.email == user_create.email)
        )
        if result.scalar_one_or_none():
            raise ConflictError("Email already registered")

        # Create user with hashed password
        user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            password_hash=hash_password(user_create.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    # ─── Login ───────────────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate user via email/password and return tokens.

        Args:
            email: User's email address.
            password: Plaintext password.

        Returns:
            TokenResponse containing access_token, token_type, and user data.

        Raises:
            UnauthorizedError (401): If credentials are invalid.
        """
        # Fetch user
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            raise UnauthorizedError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(user_id=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    # ─── Google OAuth ────────────────────────────────────────────────────

    async def google_oauth_login(
        self, code: str, redirect_uri: str
    ) -> TokenResponse:
        """Authenticate via Google OAuth authorization code.

        Exchanges the code for a Google access token, fetches the user
        profile, and upserts the user (create if new, login if exists).

        Args:
            code: Authorization code from Google OAuth flow.
            redirect_uri: The redirect URI used in the OAuth flow.

        Returns:
            TokenResponse containing access_token, token_type, and user data.

        Raises:
            UnauthorizedError (401): If the Google token exchange fails.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Exchange authorization code for access token
            token_resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                raise UnauthorizedError(
                    f"Google token exchange failed: {token_resp.text}"
                )
            token_data = token_resp.json()
            google_access_token = token_data.get("access_token")
            if not google_access_token:
                raise UnauthorizedError("No access token in Google response")

            # Fetch user profile
            profile_resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {google_access_token}"},
            )
            if profile_resp.status_code != 200:
                raise UnauthorizedError("Failed to fetch Google user profile")
            profile = profile_resp.json()

        email = profile.get("email")
        if not email:
            raise UnauthorizedError("Email not found in Google profile")

        google_id = profile.get("id")
        full_name = profile.get("name", email.split("@")[0])

        # Upsert user — find by google_id or email
        result = await self.db.execute(
            select(User).where(
                (User.google_id == google_id) | (User.email == email)
            )
        )
        user = result.scalar_one_or_none()

        if user:
            # Update google_id if not set (linking existing account)
            if not user.google_id:
                user.google_id = google_id
                await self.db.flush()
        else:
            # Create new user
            user = User(
                email=email,
                full_name=full_name,
                google_id=google_id,
                password_hash=None,  # OAuth users have no password
            )
            self.db.add(user)
            await self.db.flush()
            await self.db.refresh(user)

        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(user_id=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    # ─── Token Refresh ───────────────────────────────────────────────────

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        """Validate a refresh token and issue a new access token.

        Args:
            refresh_token_str: The encoded JWT refresh token.

        Returns:
            TokenResponse with a fresh access_token.

        Raises:
            UnauthorizedError (401): If the refresh token is invalid or user not found.
        """
        # decode_refresh_token raises 401 on failure
        payload = decode_refresh_token(refresh_token_str)
        user_id = payload.get("sub")

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedError("User not found or account deactivated")

        # Issue new tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh = create_refresh_token(user_id=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
