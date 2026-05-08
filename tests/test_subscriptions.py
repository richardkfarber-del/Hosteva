import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_checkout_session_valid_tier():
    response = client.post("/api/subscriptions/checkout", json={"tier": "pro"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert "checkout_url" in data

def test_checkout_session_invalid_tier():
    response = client.post("/api/subscriptions/checkout", json={"tier": "invalid_tier"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid tier selected"
