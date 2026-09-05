"""TE-002: eligibility must never return hash lottery GREEN/YELLOW/RED."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_eligibility_te002.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_eligibility_te002.db")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ["BILLING_ENABLED"] = "false"

from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.routers import eligibility as eligibility_mod
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_determine_status_function_removed():
    assert not hasattr(eligibility_mod, "_determine_status")


def test_check_never_returns_traffic_lights_without_maps_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    monkeypatch.delenv("Maps_API_KEY", raising=False)
    r = client.post("/api/eligibility/check", json={"address": "1 Main St, Miami Beach, FL"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] not in ("GREEN", "YELLOW", "RED")
    assert data["status"] == "UNDER_REVIEW"
    assert data.get("traffic_light_removed") is True


def test_check_with_mock_geocode_no_muni_is_under_review_not_hash(monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "fake-key")

    class FakeResp:
        def json(self):
            return {
                "status": "OK",
                "results": [
                    {
                        "formatted_address": "100 Fake St, Orlando, FL 32801, USA",
                        "address_components": [
                            {"long_name": "Orlando", "short_name": "Orlando", "types": ["locality"]},
                            {"long_name": "Florida", "short_name": "FL", "types": ["administrative_area_level_1"]},
                            {"long_name": "US", "short_name": "US", "types": ["country"]},
                        ],
                    }
                ],
            }

    with patch("app.routers.eligibility.requests.get", return_value=FakeResp()):
        # Same city many times — hash lottery would flip; we must stay stable non-traffic-light
        statuses = set()
        for _ in range(5):
            r = client.post("/api/eligibility/check", json={"address": "100 Fake St, Orlando, FL"})
            assert r.status_code == 200
            data = r.json()
            assert data["status"] not in ("GREEN", "YELLOW", "RED")
            statuses.add(data["status"])
        assert statuses <= {"UNDER_REVIEW", "NOT_COVERED", "ALLOWED_WITH_CHECKLIST", "ERROR"}
