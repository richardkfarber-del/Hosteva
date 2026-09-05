import os
import sys
import pytest
import uuid
import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Ensure Hosteva app is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode, HOARule

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_compliance_address.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_db():
    original_override = fastapi_app.dependency_overrides.get(get_db)
    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield
    if original_override is not None:
        fastapi_app.dependency_overrides[get_db] = original_override
    else:
        fastapi_app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Explicitly import all database models so they register on Base and relationships are mapped
    import app.db_models
    import app.models.memory
    import app.models.host
    import app.models.property
    import app.models.zoning
    import app.models.job
    import app.models.compliance
    import app.models.swarm
    import app.models.oauth
    import app.integrations.ota_models

    # Create all database tables in the test SQLite database
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # 1. Seed Municipal Code
        mc = MunicipalCode(
            id=uuid.uuid4(),
            municipality_name="Orange County",
            jurisdiction_type="County",
            ordinance_number="JURISDICTION-RULES",
            str_prohibited=False,
            is_allowed=True,
            requires_permit=True,
            permit_name="STR Permit",
            minimum_stay_requirement="30 days minimum stay",
            stay_restriction_days=30,
            occupancy_limits="max 10 guests",
            tax_rate=6.0,
            source_url="https://orange.county.gov/str",
            last_verified_date=datetime.date(2026, 6, 5)
        )
        db.add(mc)
        
        # 2. Seed HOA Rule
        hoa = HOARule(
            id=uuid.uuid4(),
            hoa_name="Solara Resort",
            location="Osceola County",
            str_permitted="Yes",
            minimum_lease_stay="None (Nightly)",
            rules_available=True,
            official_website="https://solararesort.com",
            last_confirmed_date=datetime.date(2026, 6, 7),
            key_rules_notes="Active resort community"
        )
        db.add(hoa)
        db.commit()
    finally:
        db.close()

    yield
    # Clean up after all tests are done
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_compliance_address.db"):
        os.remove("test_compliance_address.db")

client = TestClient(fastapi_app)

@patch("app.api.v1.compliance.geocode_address")
def test_get_compliance_by_address_success(mock_geocode):
    """
    Test GET /api/v1/compliance?address=123+Main+St
    Verifies that the endpoint successfully queries municipal_codes and hoa_rules tables
    after geocoding the address string to resolve locality components (city, county, state).
    """
    # Configure mock geocoder to return Orange County
    mock_geocode.return_value = {
        "city": "Orlando",
        "county": "Orange County",
        "state": "FL",
        "address_components": []
    }

    response = client.get("/api/v1/compliance", params={"address": "123 Main St"})
    assert response.status_code == 200
    data = response.json()
    
    # Verify response schema structure
    assert data["address"] == "123 Main St"
    assert data["is_compliant"] is True
    
    assert data["municipal_code"] is not None
    assert data["municipal_code"]["municipality_name"] == "Orange County"
    assert data["municipal_code"]["jurisdiction_type"] == "County"
    assert data["municipal_code"]["stay_restriction_days"] == 30
    assert data["municipal_code"]["tax_rate"] == 6.0
    
    assert data["hoa_rule"] is None  # Does not match location for HOA 'Osceola County'
    
    # Verify geocoding integration was called
    mock_geocode.assert_called_once_with("123 Main St")

@patch("app.api.v1.compliance.geocode_address")
def test_get_compliance_by_address_hoa_match(mock_geocode):
    """
    Test GET /api/v1/compliance?address=456+Resort+Way
    Verifies that the endpoint successfully queries and matches the HOA rule location.
    """
    # Configure mock geocoder to return Osceola County
    mock_geocode.return_value = {
        "city": "Kissimmee",
        "county": "Osceola County",
        "state": "FL",
        "address_components": []
    }

    response = client.get("/api/v1/compliance", params={"address": "456 Resort Way"})
    assert response.status_code == 200
    data = response.json()
    
    assert data["address"] == "456 Resort Way"
    assert data["municipal_code"] is None  # Does not match Orange County
    assert data["hoa_rule"] is not None
    assert data["hoa_rule"]["hoa_name"] == "Solara Resort"
    assert data["hoa_rule"]["location"] == "Osceola County"
    assert data["hoa_rule"]["minimum_lease_stay"] == "None (Nightly)"
    assert data["hoa_rule"]["rules_available"] is True
    
    mock_geocode.assert_called_once_with("456 Resort Way")

@patch("app.api.v1.compliance.geocode_address")
def test_get_compliance_by_address_not_found(mock_geocode):
    """
    Test GET /api/v1/compliance?address=999+Unknown+St
    Verifies that if no municipal code or HOA rule is found, the endpoint returns 200
    with null values, validating the schema structure.
    """
    mock_geocode.return_value = {
        "city": "Unknown City",
        "county": "Unknown County",
        "state": "FL",
        "address_components": []
    }

    response = client.get("/api/v1/compliance", params={"address": "999 Unknown St"})
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "999 Unknown St"
    # US-004: empty curated rules => Under Review, never is_compliant true
    assert data["is_under_review"] is True
    assert data["is_compliant"] is False
    assert data.get("status") == "UNDER_REVIEW"
    assert data["municipal_code"] is None
    assert data["hoa_rule"] is None
    assert data["checklist"] == []
    
    mock_geocode.assert_called_once_with("999 Unknown St")

def test_get_compliance_missing_address_parameter():
    """
    Test GET /api/v1/compliance without providing an address parameter.
    Verifies that it returns a 400 Bad Request or 422 Unprocessable Entity.
    """
    response = client.get("/api/v1/compliance")
    assert response.status_code in [400, 422]

def test_get_compliance_empty_address_parameter():
    """
    Test GET /api/v1/compliance with an empty address parameter.
    Verifies that it returns a 400 Bad Request or 422 Unprocessable Entity.
    """
    response = client.get("/api/v1/compliance", params={"address": ""})
    assert response.status_code in [400, 422]
