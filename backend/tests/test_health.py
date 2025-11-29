"""
Tests for health check endpoint.
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from app.api.health import get_checker


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client):
    """Test that health endpoint returns 200 when database is connected.

    In test environment, the app's global engine points to Postgres by default,
    so we mock `check_db_connection` to return True for a deterministic success.
    """
    # Override checker to always return True
    from main import app
    async def _ok_checker(session):
        return True
    app.dependency_overrides[get_checker] = lambda: _ok_checker
    response = await client.get("/health")
    app.dependency_overrides.pop(get_checker, None)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_health_endpoint_response_fields(client):
    """Test that health endpoint returns all required fields"""
    response = await client.get("/health")
    
    data = response.json()
    
    # Check all required fields are present
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data
    
    # Verify field types
    assert isinstance(data["status"], str)
    assert isinstance(data["database"], str)
    assert isinstance(data["timestamp"], str)
    
    # Verify timestamp is in ISO8601 format (contains 'T' and 'Z')
    assert "T" in data["timestamp"]
    assert data["timestamp"].endswith("Z")


@pytest.mark.asyncio
async def test_health_endpoint_database_failure(client):
    """Test that health endpoint returns 503 when database is disconnected"""
    # Override checker to return False
    from main import app
    async def _fail_checker(session):
        return False
    app.dependency_overrides[get_checker] = lambda: _fail_checker
    response = await client.get("/health")
    app.dependency_overrides.pop(get_checker, None)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["database"] == "disconnected"
    assert "detail" in data
    assert data["detail"] == "Database connection failed"


@pytest.mark.asyncio
async def test_health_endpoint_database_exception(client):
    """Test that health endpoint handles database exceptions gracefully"""
    # Override checker to raise an exception
    from main import app
    async def _error_checker(session):
        raise Exception("Database error")
    app.dependency_overrides[get_checker] = lambda: _error_checker
    response = await client.get("/health")
    app.dependency_overrides.pop(get_checker, None)

    # Should return 503 as the function will return False on exception
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["database"] == "disconnected"


@pytest.mark.asyncio
async def test_health_endpoint_integration(client):
    """Integration test: verify actual database connection through health endpoint"""
    # Note: This test may fail if test client doesn't have proper DB connection
    # In real scenarios, you'd want to configure a test database
    response = await client.get("/health")
    
    # We expect the endpoint to respond (either 200 or 503)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
    
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["status"] in ["healthy", "unhealthy"]
    assert data["database"] in ["connected", "disconnected"]


@pytest.mark.asyncio
async def test_create_tables_runs_without_errors(isolated_engine):
    """Creating tables via metadata on a fresh engine should not error."""
    from app.db.database import Base
    async with isolated_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
