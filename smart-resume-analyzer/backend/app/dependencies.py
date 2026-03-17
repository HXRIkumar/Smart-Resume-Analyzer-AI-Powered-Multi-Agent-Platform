"""Shared FastAPI dependencies — authentication and authorization.

Provides injectable dependencies for extracting the current user,
verifying active status, and enforcing admin role checks.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import decode_access_token

# ─── OAuth2 Scheme ───────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ─── Get Current User ────────────────────────────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT bearer token and return the authenticated user.

    Args:
        token: JWT bearer token extracted from Authorization header.
        db: Async database session.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException 401: If the token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # decode_access_token raises 401 internally on failure
    payload = decode_access_token(token)
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Ensure the token type is access (not refresh)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type — expected access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


# ─── Get Current Active User ────────────────────────────────────────────────
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the authenticated user account is active.

    Args:
        current_user: The user from get_current_user dependency.

    Returns:
        The active User object.

    Raises:
        HTTPException 403: If the user account is deactivated.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return current_user


# ─── Require Admin ──────────────────────────────────────────────────────────
async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the current user has the admin role.

    Args:
        current_user: The active user from get_current_active_user.

    Returns:
        The admin User object.

    Raises:
        HTTPException 403: If the user does not have admin privileges.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
