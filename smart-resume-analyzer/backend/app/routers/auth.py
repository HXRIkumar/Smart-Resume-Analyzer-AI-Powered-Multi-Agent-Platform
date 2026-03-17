"""Authentication router — /auth/* endpoints.

Handles user registration, email/password login, Google OAuth,
token refresh, profile retrieval, and logout.

Rate limiting: Add slowapi limiter — 5 requests/minute on /login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.auth import (
    GoogleAuthRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


# ─── POST /register ─────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new account with email/password. Returns JWT tokens and user data.",
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Register a new user and return tokens.

    - Validates email uniqueness (409 on duplicate).
    - Hashes password with bcrypt.
    - Returns access + refresh tokens.
    """
    service = AuthService(db)
    user = await service.register(user_create=data)
    # Auto-login after registration
    return await service.login(email=data.email, password=data.password)


# ─── POST /login ────────────────────────────────────────────────────────────
# Rate limiting: Add slowapi limiter — 5 requests/minute on /login

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email/password",
    description="Authenticate with email and password. Accepts both JSON body and OAuth2 form data.",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user with email/password via OAuth2 form.

    Also compatible with Swagger UI's "Authorize" button.
    The 'username' field is used as the email address.

    Raises:
        HTTPException 401: Invalid credentials.
    """
    service = AuthService(db)
    return await service.login(email=form_data.username, password=form_data.password)


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Login with JSON body",
    description="Alternative JSON-body login for frontend consumption.",
)
async def login_json(
    data: dict,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user with JSON body {email, password}.

    Raises:
        HTTPException 401: Invalid credentials.
        HTTPException 422: Missing email or password fields.
    """
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both 'email' and 'password' fields are required",
        )
    service = AuthService(db)
    return await service.login(email=email, password=password)


# ─── POST /google-login ─────────────────────────────────────────────────────

@router.post(
    "/google-login",
    response_model=TokenResponse,
    summary="Login with Google OAuth",
    description="Exchange a Google authorization code for JWT tokens. Creates account if user is new.",
)
async def google_login(
    data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate via Google OAuth authorization code flow.

    - Exchanges code for Google access token.
    - Fetches Google user profile.
    - Creates user if new, logs in if existing.

    Raises:
        HTTPException 401: Google authentication failed.
    """
    service = AuthService(db)
    return await service.google_oauth_login(
        code=data.code,
        redirect_uri=data.redirect_uri,
    )


# ─── POST /refresh ──────────────────────────────────────────────────────────

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token.",
)
async def refresh(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Issue new access + refresh tokens from a valid refresh token.

    Raises:
        HTTPException 401: Invalid or expired refresh token.
    """
    service = AuthService(db)
    return await service.refresh_token(refresh_token_str=data.refresh_token)


# ─── GET /me ────────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the authenticated user's profile. Requires a valid access token.",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Return the authenticated user's profile.

    Requires:
        Valid Bearer token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


# ─── POST /logout ───────────────────────────────────────────────────────────

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Client-side logout instruction. Discard tokens on the client.",
)
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Log out the current user.

    Since JWTs are stateless, the client should:
    1. Delete the access token from localStorage/memory.
    2. Delete the refresh token.
    3. Redirect to /login.

    Returns:
        Success message with logout instructions.
    """
    return {
        "message": "Successfully logged out",
        "instruction": "Delete access_token and refresh_token on the client side",
    }
