import os
# Force SQLite test URL globally for all tests BEFORE any app models/modules are imported
os.environ["DATABASE_URL"] = "sqlite:///./test_validation_workflow.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_validation_workflow.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.main import app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode, Region, ZoningCode, ComplianceRule, PropertyCompliance
from app.models.property import Property

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_validation_workflow.db"
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
def setup_test_db():
    # Create all database tables in the test SQLite database
    Base.metadata.create_all(bind=engine)
    
    # Seed dynamic rules for Hillsborough, St. Pete, and Pasco
    db = TestingSessionLocal()
    try:
        # 1. State of Florida rule
        db.add(MunicipalCode(
            municipality_name="State of Florida",
            ordinance_number="FL-STATE-LICENSE",
            str_prohibited=False,
            requires_permit=True,
            permit_name="DBPR Vacation Rental License (Dwelling or Condominium)"
        ))

        # 2. Hillsborough County rule
        db.add(MunicipalCode(
            municipality_name="Hillsborough County",
            ordinance_number="HILLSBOROUGH-MIN-STAY",
            str_prohibited=False,
            stay_restriction_days=7,
            tax_rate=6.0
        ))

        # 3. City of St. Petersburg rule
        db.add(MunicipalCode(
            municipality_name="City of St. Petersburg",
            ordinance_number="ST-PETE-FREQ-LIMIT",
            str_prohibited=False,
            max_rentals_per_year=3
        ))

        # 4. Pasco County rule
        db.add(MunicipalCode(
            municipality_name="Pasco County",
            ordinance_number="PASCO-PERMIT-REQ",
            str_prohibited=False,
            requires_permit=True,
            permit_name="Conditional Use Permit (CUP)",
            tax_rate=4.0
        ))

        db.commit()
    finally:
        db.close()

    yield
    # Clean up after all tests are done
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_validation_workflow.db"):
        os.remove("test_validation_workflow.db")

client = TestClient(app)

def test_hillsborough_nightly_reject():
    """
    Hillsborough County / Tampa: nightly (fewer than 7 nights) stays should be blocked.
    """
    payload = {
        "property_id": 101,
        "city": "Tampa",
        "zip_code": "33602",
        "zoning_code": "RS-50",
        "property_type": "Single-Family",
        "intended_stay_duration": "nightly"
    }
    response = client.post("/api/v1/onboarding/validate-property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is False
    assert "Hillsborough County Land Development Code" in data["reason"]

def test_hillsborough_weekly_allowed_and_checklist():
    """
    Hillsborough County / Tampa: weekly stays are allowed and generate the Hillsborough checklist.
    """
    db = TestingSessionLocal()
    # Ensure any prior records are cleared
    db.query(PropertyCompliance).delete()
    db.query(Property).delete()
    db.commit()
    db.close()

    payload = {
        "property_id": 102,
        "city": "Tampa",
        "zip_code": "33602",
        "zoning_code": "RS-50",
        "property_type": "Single-Family",
        "intended_stay_duration": "weekly"
    }
    response = client.post("/api/v1/onboarding/validate-property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True

    # Verify checklist entries in property_compliance
    db = TestingSessionLocal()
    compliance_items = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == "102").all()
    assert len(compliance_items) == 3
    notes = [item.violation_notes for item in compliance_items]
    assert "Florida DBPR License task" in notes
    assert "Hillsborough 6% Tourist Development Tax (TDT) registration" in notes
    assert "State Sales Tax registration" in notes
    db.close()

def test_st_petersburg_warning_and_checklist():
    """
    St. Petersburg: stays are allowed with a warning and generate the St. Pete checklist.
    """
    db = TestingSessionLocal()
    db.query(PropertyCompliance).delete()
    db.query(Property).delete()
    db.commit()
    db.close()

    payload = {
        "property_id": 103,
        "city": "St. Petersburg",
        "zip_code": "33701",
        "zoning_code": "NT-1",
        "property_type": "Condo",
        "intended_stay_duration": "nightly"
    }
    response = client.post("/api/v1/onboarding/validate-property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert "St. Petersburg limits short-term rentals" in data["warning"]

    # Verify checklist entries in property_compliance
    db = TestingSessionLocal()
    compliance_items = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == "103").all()
    assert len(compliance_items) == 4
    notes = [item.violation_notes for item in compliance_items]
    assert "Florida DBPR License task" in notes
    assert "St. Petersburg Business Tax Receipt (BTR) task" in notes
    assert "Pinellas 6% TDT registration" in notes
    assert "State Sales Tax registration" in notes
    db.close()

def test_pasco_county_permit_and_checklist():
    """
    Pasco County: stays are allowed but require a CUP permit and generate the Pasco checklist.
    """
    db = TestingSessionLocal()
    db.query(PropertyCompliance).delete()
    db.query(Property).delete()
    db.commit()
    db.close()

    payload = {
        "property_id": 104,
        "city": "New Port Richey",
        "zip_code": "34652",
        "zoning_code": "R-4",
        "property_type": "Single-Family",
        "intended_stay_duration": "nightly"
    }
    response = client.post("/api/v1/onboarding/validate-property", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert data["requires_permit"] is True
    assert data["permit_name"] == "Conditional Use Permit (CUP)"

    # Verify checklist entries in property_compliance
    db = TestingSessionLocal()
    compliance_items = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == "104").all()
    assert len(compliance_items) == 4
    notes = [item.violation_notes for item in compliance_items]
    assert "Pasco Conditional Use Permit task" in notes
    assert "Annual Growth Management Registration" in notes
    assert "Pasco 4% TDT registration" in notes
    assert "State Sales Tax registration" in notes
    db.close()
