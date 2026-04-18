"""
Test Suite for MVP Dashboard API (GET /api/v1/properties)
Implements FEAT-019 TDD Mandate verifying PII masking, 401s, and 503s.
Architectured and verified by Iron Man.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
import asyncio
from app.core.security import get_current_user

client = TestClient(app)

def mock_get_current_user():
    return {"username": "testuser"}

def test_api_properties_pii_masking():
    # Override auth for this test
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    with patch("app.api.routes.properties.aggregate_properties", new_callable=AsyncMock) as mock_agg:
        mock_agg.return_value = {
            "properties": [
                {
                    "id": "prop_test123",
                    "address": {
                        "full_string": "123 Test St",
                        "zip_code": "12345"
                    },
                    "property_type": "House",
                    "compliance_progress": {
                        "completed": 2,
                        "total": 5,
                        "percentage": 40.0
                    },
                    "status_badge": "pending",
                    "compliance_id": "999-88-7777"
                }
            ],
            "meta": {
                "total_properties": 1,
                "platform_adoption_metrics": {
                    "airbnb_linked": False,
                    "vrbo_linked": False
                }
            }
        }
        response = client.get("/api/v1/properties")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["properties"]) > 0
        
        # PII Masking validation
        compliance_id = data["properties"][0]["compliance_id"]
        assert compliance_id == "***-**-7777"
        assert len(compliance_id) == 11

    app.dependency_overrides.clear()

def test_api_properties_unauthorized_401():
    # Do not mock auth, should return 401
    response = client.get("/api/v1/properties")
    assert response.status_code == 401

def test_api_properties_timeout_503():
    # Override auth for this test
    app.dependency_overrides[get_current_user] = mock_get_current_user

    with patch("app.api.routes.properties.aggregate_properties") as mock_agg:
        mock_agg.side_effect = asyncio.TimeoutError
        
        response = client.get("/api/v1/properties")
        assert response.status_code == 503
        data = response.json()
        assert "System Degraded" in data["detail"]

    app.dependency_overrides.clear()