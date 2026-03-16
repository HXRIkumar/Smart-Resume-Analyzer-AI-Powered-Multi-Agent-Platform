"""Tests for resume endpoints."""

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
async def test_list_resumes_unauthorized(client: AsyncClient):
    """Test listing resumes without auth returns 401."""
    response = await client.get("/resume/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_resume_unauthorized(client: AsyncClient):
    """Test uploading resume without auth returns 401."""
    response = await client.post(
        "/resume/upload",
        files={"file": ("test.pdf", b"%PDF-1.4 fake content", "application/pdf")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_resume_not_found(client: AsyncClient):
    """Test getting nonexistent resume returns 401 (no auth)."""
    response = await client.get("/resume/99999")
    assert response.status_code == 401
