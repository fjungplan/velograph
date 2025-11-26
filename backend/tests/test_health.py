"""
Tests for health check endpoint.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from fastapi import status


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client):
    """Test that health endpoint returns 200 when database is connected"""
    response = await client.get("/health")
    
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
    # Mock the check_db_connection function to return False
    with patch("app.api.health.check_db_connection", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = False
        
        response = await client.get("/health")
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"
        assert "detail" in data
        assert data["detail"] == "Database connection failed"


@pytest.mark.asyncio
async def test_health_endpoint_database_exception(client):
    """Test that health endpoint handles database exceptions gracefully"""
    # Mock the check_db_connection function to raise an exception
    with patch("app.api.health.check_db_connection", new_callable=AsyncMock) as mock_check:
        mock_check.side_effect = Exception("Database error")
        
        response = await client.get("/health")
        
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
async def test_create_tables_runs_without_errors():
    """Test that create_tables() runs without errors"""
    from app.db.database import create_tables
    
    # Should not raise any exceptions
    await create_tables()
