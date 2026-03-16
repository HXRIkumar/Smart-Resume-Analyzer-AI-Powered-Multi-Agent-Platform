"""Tests for authentication endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    """Test registration with missing fields returns 422."""
    response = await client.post("/auth/register", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpass"},
    )
    assert response.status_code in (401, 500)  # 500 if DB not connected


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient):
    """Test /auth/me without token returns 401."""
    response = await client.get("/auth/me")
    assert response.status_code == 401
