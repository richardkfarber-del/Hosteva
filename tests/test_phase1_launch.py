import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base, get_db
from app.db_models import WaitlistLead, Subscription
from app.models.host import Host

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_terms_of_service_page():
    response = client.get("/terms")
    assert response.status_code == 200
    assert "Hosteva Terms of Service" in response.text
    assert "NOT LEGAL, TAX, OR PROFESSIONAL ADVICE" in response.text
    assert "Hosteva is an automated compliance research and management tool" in response.text

def test_privacy_policy_page():
    response = client.get("/privacy")
    assert response.status_code == 200
    assert "Hosteva Privacy Policy" in response.text
    assert "No Selling of Personal Data" in response.text
    assert "AI Model Training Protections" in response.text

def test_features_redirect():
    response = client.get("/features", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/#features"

def test_waitlist_submission_success():
    payload = {
        "email": "phase1_test_host@example.com",
        "portfolio_size": "3-5",
        "tier_interest": "PHASE_2_AUTOMATION"
    }
    response = client.post("/api/v1/waitlist/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "Thank you for joining" in data["message"]
    assert "id" in data

def test_waitlist_submission_invalid_email():
    payload = {
        "email": "invalid-email",
        "portfolio_size": "1-2"
    }
    response = client.post("/api/v1/waitlist/", json=payload)
    assert response.status_code == 400
    assert "valid email" in response.json()["detail"]

def test_landing_page_compliance_tiers_and_disclaimer():
    response = client.get("/")
    assert response.status_code == 200
    assert "Transparent Compliance Tiers" in response.text
    assert "Compliance Essentials" in response.text
    assert "$9.99" in response.text
    assert "Automation Suite" in response.text
    assert "Join Phase II Waitlist" in response.text
    assert "Hosteva is an automated compliance research and management tool" in response.text

@patch("app.api.v1.compliance.geocode_address")
def test_compliance_address_under_review_flag(mock_geocode):
    mock_geocode.return_value = {
        "city": "Unincorporated Lee County",
        "county": "Lee County",
        "state": "FL",
        "zip_code": "33999",
        "latitude": 26.5,
        "longitude": -81.8
    }
    response = client.get("/api/v1/compliance?address=123+Unknown+Trail,+Unincorporated,+FL+33999")
    assert response.status_code == 200
    data = response.json()
    assert "is_under_review" in data
    assert data["is_under_review"] is True
    assert data["is_compliant"] is False  # US-004: never Compliant/GREEN when under review
    assert data.get("status") in (None, "UNDER_REVIEW") or data.get("status") == "UNDER_REVIEW"
    assert "checklist" in data

def test_user_profile_and_sidebar_widget_flow():
    # 1. Register a new user
    reg_payload = {
        "username": "widget_qa_host",
        "email": "widget_qa_host@example.com",
        "password": "Password123!"
    }
    reg_resp = client.post("/api/user/register", json=reg_payload)
    assert reg_resp.status_code == 200

    # 2. Login to get token and cookie
    login_resp = client.post("/api/user/login", data={"username": "widget_qa_host", "password": "Password123!"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 3. Test /api/v1/users/me with Bearer token
    me_resp = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == "widget_qa_host"
    assert me_data["tier"] == "Free Tier"
    assert me_data["has_active_subscription"] is False

    # 4. Test /api/v1/billing/checkout with COMPLIANCE_ESSENTIALS tier
    checkout_resp = client.post(
        "/api/v1/billing/checkout",
        headers={"Authorization": f"Bearer {token}"},
        json={"tier": "COMPLIANCE_ESSENTIALS"}
    )
    assert checkout_resp.status_code == 200
    checkout_data = checkout_resp.json()
    assert "checkout_url" in checkout_data
