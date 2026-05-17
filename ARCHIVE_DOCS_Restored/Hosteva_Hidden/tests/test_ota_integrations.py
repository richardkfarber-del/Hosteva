import pytest
from fastapi.testclient import TestClient

# Adjust this import to match the actual entrypoint of your FastAPI app
from app.main import app

client = TestClient(app)

VALID_PROVIDER = "airbnb"
INVALID_PROVIDER = "unknown_provider"

# --- Tests for /auth endpoint ---

def test_ota_auth_success():
    """Test successful generation of the OAuth authorization URL."""
    response = client.get(f"/api/v1/integrations/ota/{VALID_PROVIDER}/auth")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data or "auth_url" in data

def test_ota_auth_invalid_provider():
    """Test /auth with an unsupported provider."""
    response = client.get(f"/api/v1/integrations/ota/{INVALID_PROVIDER}/auth")
    assert response.status_code == 400
    # E.g., assert "Invalid provider" in response.json()["detail"]

# --- Tests for /callback endpoint ---

def test_ota_callback_success():
    """Test successful handling of the OAuth callback with a valid code."""
    response = client.get(f"/api/v1/integrations/ota/{VALID_PROVIDER}/callback?code=test_auth_code_123")
    assert response.status_code == 200
    # Expected success payload validation

def test_ota_callback_missing_code():
    """Test /callback when the required 'code' query parameter is missing."""
    response = client.get(f"/api/v1/integrations/ota/{VALID_PROVIDER}/callback")
    # Depending on implementation, missing query params often trigger 422 Validation Error or custom 400
    assert response.status_code in [400, 422]

def test_ota_callback_invalid_provider():
    """Test /callback with an unsupported provider."""
    response = client.get(f"/api/v1/integrations/ota/{INVALID_PROVIDER}/callback?code=test_auth_code_123")
    assert response.status_code == 400

# --- Tests for /sync endpoint ---

def test_ota_sync_success():
    """Test successful triggering of an OTA data sync."""
    response = client.post(f"/api/v1/integrations/ota/{VALID_PROVIDER}/sync")
    assert response.status_code in [200, 202] # 202 if async background task
    data = response.json()
    assert data.get("status") in ["success", "sync_started", "queued", "accepted"]

def test_ota_sync_invalid_provider():
    """Test /sync with an unsupported provider."""
    response = client.post(f"/api/v1/integrations/ota/{INVALID_PROVIDER}/sync")
    assert response.status_code == 400
