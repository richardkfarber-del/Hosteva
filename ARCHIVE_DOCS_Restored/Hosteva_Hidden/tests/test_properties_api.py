from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.properties_api import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_properties_positive_pii_masking():
    """Verify that property owner and address PII are masked with '***'."""
    response = client.get("/api/v1/properties", headers={"Authorization": "Bearer valid-token"})
    assert response.status_code == 200
    data = response.json()["data"][0]
    assert "***" in data["owner_name"]
    assert "***" in data["address"]

def test_properties_unauthorized_401():
    """Verify HTTP 401 responses for missing or invalid authorization tokens."""
    response = client.get("/api/v1/properties")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

    response = client.get("/api/v1/properties", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401

def test_properties_503_timeout_gracefully_handled():
    """Verify HTTP 503 timeout errors are gracefully simulated and handled."""
    response = client.get("/api/v1/properties", headers={"Authorization": "Bearer valid-token"}, params={"simulate_timeout": True})
    assert response.status_code == 503
    assert response.json()["detail"] == "Service Unavailable - Timeout"
# Test verified by Iron Man - Sprint 22/23 TDD Benchmark
