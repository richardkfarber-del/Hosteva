import os
# Force SQLite test URL globally for all tests BEFORE any app models/modules are imported
os.environ["DATABASE_URL"] = "sqlite:///./test_validation.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_validation.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode, Region, ZoningCode, ComplianceRule

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_validation.db"
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
    original_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    yield
    if original_override is not None:
        app.dependency_overrides[get_db] = original_override
    else:
        app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="module", autouse=True)
def setup_validation_db():
    # Create all database tables in the test SQLite database
    Base.metadata.create_all(bind=engine)
    
    # Seed dynamic, location-agnostic rules for testing
    db = TestingSessionLocal()
    try:
        # Seed Region for Faketown (with admin_area = "FK")
        r1 = Region(locality="Fakestate", admin_area="FK")
        r2 = Region(locality="Faketown", admin_area="FK")
        db.add_all([r1, r2])
        db.commit()

        # 1. State Level rule (State of Fakestate)
        fl_mcode = MunicipalCode(
            municipality_name="State of Fakestate",
            ordinance_number="FK-STATE-LICENSE",
            str_prohibited=False,
            requires_permit=True,
            permit_name="Fakestate License"
        )
        db.add(fl_mcode)

        # 2. County Level rule (Fakecounty County)
        md_mcode = MunicipalCode(
            municipality_name="Fakecounty County",
            ordinance_number="FK-COUNTY-CU",
            str_prohibited=False,
            requires_permit=True,
            permit_name="Fakecounty CU",
            tax_rate=5.5
        )
        db.add(md_mcode)

        # 3. City Level rule (City of Faketown) - generally allowed, no restrictions
        mb_mcode = MunicipalCode(
            municipality_name="City of Faketown",
            ordinance_number="FK-CITY-OK",
            str_prohibited=False
        )
        db.add(mb_mcode)

        # 4. Prohibited Zoning Rule (City of Faketown, Zoning F-1)
        zoning_rule = MunicipalCode(
            municipality_name="City of Faketown",
            ordinance_number="FK-ZONING-PROHIBITED",
            is_allowed=False,
            zoning_code="F-1",
            rejection_reason="Zoning F-1 is not permitted for short term rentals",
            source_url="http://fake.gov/zoning"
        )
        db.add(zoning_rule)

        # 5. Prohibited Property Type Rule (City of Faketown, Property Type Single-Family)
        prop_rule = MunicipalCode(
            municipality_name="City of Faketown",
            ordinance_number="FK-PROP-PROHIBITED",
            is_allowed=False,
            property_type="Single-Family",
            rejection_reason="Single-Family homes cannot be rented short term",
            source_url="http://fake.gov/prop"
        )
        db.add(prop_rule)

        # 6. Minimum Stay Duration Rule (City of Faketown, min stay 12 days)
        stay_rule = MunicipalCode(
            municipality_name="City of Faketown",
            ordinance_number="FK-STAY-LIMIT",
            stay_restriction_days=12,
            source_url="http://fake.gov/stay"
        )
        db.add(stay_rule)

        db.commit()
    finally:
        db.close()

    yield
    # Clean up after all tests are done
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_validation.db"):
        os.remove("test_validation.db")

client = TestClient(app)

def test_validate_property_agnostic_reject_zoning():
    """
    Check if the property zoning_code matches a restricted zoning rule.
    """
    payload = {
        "city": "Faketown",
        "county": "Fakecounty",
        "zip_code": "99999",
        "zoning_code": "F-1",
        "property_type": "Condo",
        "requested_stay_duration_days": 30
    }
    response = client.post("/api/v1/onboarding/validate-property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is False
    assert data["status"] == "REJECTED"
    assert data["rejection_reason"] == "Zoning F-1 is not permitted for short term rentals"
    assert data["source_url"] == "http://fake.gov/zoning"

def test_validate_property_agnostic_reject_property_type():
    """
    Check if the property property_type matches a restricted property type rule.
    """
    payload = {
        "city": "Faketown",
        "county": "Fakecounty",
        "zip_code": "99999",
        "zoning_code": "F-2",
        "property_type": "Single-Family",
        "requested_stay_duration_days": 30
    }
    response = client.post("/api/v1/onboarding/validate-property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is False
    assert data["status"] == "REJECTED"
    assert data["rejection_reason"] == "Single-Family homes cannot be rented short term"
    assert data["source_url"] == "http://fake.gov/prop"

def test_validate_property_agnostic_reject_stay_duration():
    """
    Check if the requested stay duration is less than the minimum required stay.
    """
    payload = {
        "city": "Faketown",
        "county": "Fakecounty",
        "zip_code": "99999",
        "zoning_code": "F-2",
        "property_type": "Condo",
        "requested_stay_duration_days": 5
    }
    response = client.post("/api/v1/onboarding/validate-property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is False
    assert data["status"] == "REJECTED"
    assert data["rejection_reason"] == "Requested stay duration is less than the minimum required stay of 12 days"
    assert data["source_url"] == "http://fake.gov/stay"

def test_validate_property_agnostic_allowed_checklist_generation():
    """
    If no rules are violated, return allowed=True and the generated checklist.
    """
    payload = {
        "city": "Faketown",
        "county": "Fakecounty",
        "zip_code": "99999",
        "zoning_code": "F-2",
        "property_type": "Condo",
        "requested_stay_duration_days": 30
    }
    response = client.post("/api/v1/onboarding/validate-property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert data["status"] == "PASSED"
    assert "checklist" in data
    checklist = data["checklist"]
    assert len(checklist) >= 3
    
    # State level permit check
    state_item = next((item for item in checklist if item["level"] == "State"), None)
    assert state_item is not None
    assert state_item["authority"] == "State of Fakestate"
    assert state_item["requirement"] == "Fakestate License"

    # County level permit check
    county_item = next((item for item in checklist if item["level"] == "County" and "CU" in item["requirement"]), None)
    assert county_item is not None
    assert county_item["authority"] == "Fakecounty County"
    assert county_item["requirement"] == "Fakecounty CU"

    # County level tax check
    tax_item = next((item for item in checklist if item["level"] == "County" and "TDT" in item["requirement"]), None)
    assert tax_item is not None
    assert tax_item["authority"] == "Fakecounty County"
    assert "5.5% TDT" in tax_item["requirement"]
