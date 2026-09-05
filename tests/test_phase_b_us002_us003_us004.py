"""Phase B US-002 / US-003 / US-004 focused regression tests."""
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_phase_b_us002_003_004.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_phase_b_us002_003_004.db"

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode
import app.db_models  # noqa: F401

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_phase_b_us002_003_004.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add(MunicipalCode(
            municipality_name="Bay County",
            ordinance_number="BAY-STR-INSPECT",
            jurisdiction_type="County",
            state="FL",
            str_prohibited=False,
            is_allowed=True,
            requires_permit=True,
            permit_name="Short-Term Vacation Rental Inspection",
            tax_rate=5.0,
            source_url="https://www.baycountyfl.gov/783/Short-Term-Vacation-Rental-Inspections",
        ))
        db.add(MunicipalCode(
            municipality_name="Broward County",
            ordinance_number="BROWARD-RRC",
            jurisdiction_type="County",
            state="FL",
            str_prohibited=False,
            is_allowed=True,
            requires_permit=True,
            permit_name="Residential Rental Certificate",
            source_url="https://www.broward.org/Planning/CodeEnforcement/Pages/ResRentCert.aspx",
        ))
        db.add(MunicipalCode(
            municipality_name="Miami Beach",
            ordinance_number="MB-STR-PROHIBITION",
            jurisdiction_type="City",
            state="FL",
            str_prohibited=True,
            is_allowed=False,
            requires_permit=True,
            permit_name="Miami Beach STR Certificate / Zoning Review",
            source_url="https://www.miamibeachfl.gov/government/planning/zoning/",
        ))
        db.commit()
    finally:
        db.close()
    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield
    fastapi_app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_phase_b_us002_003_004.db"):
        os.remove("test_phase_b_us002_003_004.db")


client = TestClient(fastapi_app)


# --- US-004 ---
@patch("app.api.v1.compliance.geocode_address")
def test_under_review_never_is_compliant_true(mock_geocode):
    mock_geocode.return_value = {
        "city": "Unknownville",
        "county": "Nowhere County",
        "state": "FL",
        "address_components": [],
    }
    res = client.get("/api/v1/compliance", params={"address": "1 Nowhere Ln, FL"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_under_review"] is True
    assert data["is_compliant"] is False
    assert data.get("status") == "UNDER_REVIEW"
    assert data.get("status") != "GREEN"
    assert "GREEN" not in str(data.get("status", "")).upper() or data["status"] == "UNDER_REVIEW"


@patch("app.api.v1.compliance.geocode_address")
def test_miami_beach_covered_not_under_review(mock_geocode):
    """SP-001 UAT-3: Miami Beach pack must be Covered for Free Audit."""
    mock_geocode.return_value = {
        "city": "Miami Beach",
        "county": "Miami-Dade County",
        "state": "FL",
        "address_components": [],
    }
    res = client.get(
        "/api/v1/compliance",
        params={"address": "1700 Convention Center Dr, Miami Beach, FL 33139"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_under_review"] is False
    assert data["municipal_code"] is not None
    assert "Miami Beach" in data["municipal_code"]["municipality_name"]
    assert data["is_compliant"] is False  # prohibited pack
    assert data["municipal_code"].get("source_url")


# --- US-003 ---
@patch("app.api.v1.compliance.geocode_address")
def test_bay_county_checklist_includes_gov_source_url(mock_geocode):
    mock_geocode.return_value = {
        "city": "Panama City",
        "county": "Bay County",
        "state": "FL",
        "address_components": [],
    }
    res = client.get(
        "/api/v1/compliance",
        params={"address": "17001 Panama City Beach Pkwy, Panama City Beach, FL 32413"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_under_review"] is False
    assert data["municipal_code"] is not None
    assert data["municipal_code"]["source_url"]
    assert ".gov" in data["municipal_code"]["source_url"] or "baycountyfl.gov" in data["municipal_code"]["source_url"]
    assert data["checklist"]
    assert any(item.get("source_url") for item in data["checklist"])


@patch("app.api.v1.compliance.geocode_address")
def test_broward_checklist_cites_official_source(mock_geocode):
    mock_geocode.return_value = {
        "city": "",
        "county": "Broward County",
        "state": "FL",
        "address_components": [],
    }
    res = client.get("/api/v1/compliance", params={"address": "1 Broward Blvd, FL"})
    assert res.status_code == 200
    data = res.json()
    assert data["municipal_code"]["municipality_name"] == "Broward County"
    assert data["municipal_code"]["source_url"]
    assert "broward.org" in data["municipal_code"]["source_url"] or ".gov" in data["municipal_code"]["source_url"]
    for item in data["checklist"]:
        assert "source_url" in item


# --- US-002 (template / handoff contract) ---
def test_wizard_register_dashboard_address_handoff_markers():
    wiz = client.get("/wizard")
    assert wiz.status_code == 200
    assert "pending_property_address" in wiz.text
    assert "/register?address=" in wiz.text

    reg = client.get("/register?address=301%20E%20Dakin%20Ave%2C%20Kissimmee%2C%20FL%2034741")
    assert reg.status_code == 200
    assert "initial_address=" in reg.text
    assert "pending_property_address" in reg.text
    assert "property-pending-banner" in reg.text

    dash = client.get("/dashboard")
    assert dash.status_code == 200
    assert "Add this property?" in dash.text or "pending_property_address" in dash.text
    assert "initial_address" in dash.text
