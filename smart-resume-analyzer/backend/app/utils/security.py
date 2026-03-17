"""Security utilities — password hashing, JWT access/refresh tokens.

Production-grade implementation using bcrypt + python-jose (HS256).
All token operations include proper error handling and expiration.
"""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# ─── Password Hashing ───────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token lifetimes
ACCESS_TOKEN_EXPIRE = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: The plaintext password to hash.

    Returns:
        The bcrypt-hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash.

    Args:
        plain_password: The plaintext password to verify.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a short-lived JWT access token.

    Args:
        data: Claims to encode. Must include 'sub' (user id).
        expires_delta: Custom expiration. Defaults to ACCESS_TOKEN_EXPIRE.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or ACCESS_TOKEN_EXPIRE)
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access",
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived JWT refresh token (7-day expiry).

    Args:
        user_id: The user's UUID as a string.

    Returns:
        Encoded JWT refresh token string.
    """
    now = datetime.now(timezone.utc)
    to_encode = {
        "sub": user_id,
        "exp": now + REFRESH_TOKEN_EXPIRE,
        "iat": now,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.

    Args:
        token: The encoded JWT string.

    Returns:
        The decoded payload dictionary.

    Raises:
        HTTPException 401: If the token is expired, invalid, or malformed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_refresh_token(token: str) -> dict:
    """Decode and validate a JWT refresh token.

    Args:
        token: The encoded JWT refresh token string.

    Returns:
        The decoded payload dictionary.

    Raises:
        HTTPException 401: If the token is expired, invalid, or not a refresh token.
    """
    payload = decode_access_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type — expected refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
