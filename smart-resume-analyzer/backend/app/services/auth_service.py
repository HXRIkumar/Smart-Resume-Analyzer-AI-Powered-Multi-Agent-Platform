"""Authentication service — JWT + OAuth logic."""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.config import settings
from app.models.user import User
from app.utils.exceptions import ConflictError, UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handles user registration, authentication, and JWT management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, full_name: str, password: str) -> User:
        """Register a new local user."""
        existing = await self.db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ConflictError("Email already registered")

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=pwd_context.hash(password),
            auth_provider="local",
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        """Verify email/password and return user if valid."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not user.hashed_password:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    async def google_authenticate(self, id_token: str) -> User:
        """Verify Google ID token and create/get user."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            if resp.status_code != 200:
                raise UnauthorizedError("Invalid Google token")
            data = resp.json()

        email = data.get("email")
        if not email:
            raise UnauthorizedError("Email not found in Google token")

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                email=email,
                full_name=data.get("name", email.split("@")[0]),
                auth_provider="google",
            )
            self.db.add(user)
            await self.db.flush()
            await self.db.refresh(user)

        return user

    @staticmethod
    def create_token(user: User) -> str:
        """Create a JWT access token."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
