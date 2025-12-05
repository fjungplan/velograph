from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns expected response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
    assert "version" in data


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    # Health endpoint may return 200 or 503 depending on DB availability in test context
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data


def test_app_startup():
    """Test that the FastAPI app starts successfully"""
    assert app.title == "ChainLines API"
    assert app.version == "0.1.0"
