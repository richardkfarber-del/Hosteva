"""US-010: /features and /about are real pages with Florida-depth positioning.

BUG-PL-04: competitor brand names scrubbed from customer-facing Features/About.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_us010_pages.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_us010_pages.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-us010")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

COMPETITOR_NAMES = ("HostReady", "PermitGuard", "Guesty", "Lodge Compliance", "Hostaway")


def test_features_http_200_not_redirect():
    r = client.get("/features", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    assert "Florida checklist depth" in body
    assert "built for hosts, not for busywork" in body
    assert "operations engine" in body.lower()
    assert "Under Review" in body
    assert "$9.99" in body and "$99" in body
    assert "not legal" in body.lower() or "does not provide legal advice" in body.lower()
    for name in COMPETITOR_NAMES:
        assert name not in body


def test_about_http_200():
    r = client.get("/about", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    assert "About Hosteva" in body
    assert "other compliance tools" in body
    assert "property-management system" in body.lower() or "PMS" in body
    assert "Under Review" in body
    assert "does not provide legal advice" in body.lower() or "not provide legal advice" in body.lower()
    for name in COMPETITOR_NAMES:
        assert name not in body
    # Historical internal nickname must not reappear
    assert "HostReady Bubble" not in body
    assert "Bubble" not in body


def test_no_operations_engine_as_live_claim():
    for path in ("/features", "/about"):
        body = client.get(path).text.lower()
        # Must not claim live ops engine; may say we do NOT market as one
        assert "not" in body and "operations engine" in body


def test_features_about_meta_scrubbed():
    for path in ("/features", "/about"):
        body = client.get(path).text
        for name in COMPETITOR_NAMES:
            assert name not in body
