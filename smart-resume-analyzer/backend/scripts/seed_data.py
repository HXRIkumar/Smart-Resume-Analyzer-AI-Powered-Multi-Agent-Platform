"""
Seed script — populates the database with an admin user and 3 test users.

Usage:
    docker-compose exec backend python scripts/seed_data.py
    # or locally:
    cd backend && python scripts/seed_data.py

Creates:
    - admin@smartresume.com / Admin123!  (role: admin)
    - alice@example.com / TestUser1!     (role: user)
    - bob@example.com / TestUser2!       (role: user)
    - carol@example.com / TestUser3!     (role: user)
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime, timezone

# Ensure the backend app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import async_session_maker, engine
from app.models.user import User, UserRole

# Bcrypt-compatible password hashing
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def hash_password(pw: str) -> str:
        return pwd_context.hash(pw)
except ImportError:
    import hashlib
    def hash_password(pw: str) -> str:
        return hashlib.sha256(pw.encode()).hexdigest()


USERS = [
    {
        "full_name": "Admin User",
        "email": "admin@smartresume.com",
        "password": "Admin123!",
        "role": UserRole.ADMIN,
    },
    {
        "full_name": "Alice Johnson",
        "email": "alice@example.com",
        "password": "TestUser1!",
        "role": UserRole.USER,
    },
    {
        "full_name": "Bob Smith",
        "email": "bob@example.com",
        "password": "TestUser2!",
        "role": UserRole.USER,
    },
    {
        "full_name": "Carol Williams",
        "email": "carol@example.com",
        "password": "TestUser3!",
        "role": UserRole.USER,
    },
]


async def seed():
    """Create seed users if they don't already exist."""
    print("\n" + "=" * 55)
    print("  Smart Resume Analyzer — Database Seeder")
    print("=" * 55 + "\n")

    async with async_session_maker() as session:
        created = 0
        skipped = 0

        for user_data in USERS:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ⏭  {user_data['email']:30s}  — already exists")
                skipped += 1
                continue

            user = User(
                id=uuid.uuid4(),
                full_name=user_data["full_name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                auth_provider="local",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(user)
            print(f"  ✅  {user_data['email']:30s}  — created ({user_data['role'].value})")
            created += 1

        await session.commit()

    print(f"\n  Summary: {created} created, {skipped} skipped")
    print("\n" + "-" * 55)
    print("  Login Credentials:")
    print("-" * 55)
    for user_data in USERS:
        role_badge = "👑 ADMIN" if user_data["role"] == UserRole.ADMIN else "  user "
        print(f"  {role_badge}  {user_data['email']:30s}  {user_data['password']}")
    print("-" * 55 + "\n")


if __name__ == "__main__":
    asyncio.run(seed())
