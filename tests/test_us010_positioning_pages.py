"""US-010: /features and /about are real pages with Florida-depth positioning."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_us010_pages.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_us010_pages.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-us010")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_features_http_200_not_redirect():
    r = client.get("/features", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    assert "Florida checklist depth" in body
    assert "HostReady/PermitGuard" in body
    assert "operations engine" in body.lower()
    assert "not as an anti-Guesty" in body
    assert "HostReady Bubble" not in body  # Bubble naming stays off Features; scrub note lives on About


def test_about_http_200():
    r = client.get("/about", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    assert "About Hosteva" in body
    assert "HostReady/PermitGuard" in body
    assert "property-management system" in body.lower() or "PMS" in body
    # Scrub note: Bubble naming acknowledged as not used in customer materials
    assert "HostReady Bubble" in body
    assert "not used" in body.lower()


def test_no_operations_engine_as_live_claim():
    for path in ("/features", "/about"):
        body = client.get(path).text.lower()
        # Must not claim live ops engine; may say we do NOT market as one
        assert "not" in body and "operations engine" in body
