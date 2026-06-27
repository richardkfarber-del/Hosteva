import os
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

# Force SQLite test URL globally for all tests BEFORE any app models/modules are imported
os.environ["DATABASE_URL"] = "sqlite:///./test_compliance_endpoint.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_compliance_endpoint.db"

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode, PropertyCompliance
from app.models.property import Property
from app.models.host import Host
import app.db_models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_compliance_endpoint.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def mock_geocode():
    with patch("app.api.v1.compliance.geocode_address") as mock:
        def side_effect(address):
            if address == "123 Main St":
                return {"city": "Miami", "county": "Miami-Dade County", "state": "FL", "address_components": []}
            return {"city": "", "county": "", "state": "", "address_components": []}
        mock.side_effect = side_effect
        yield mock


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
    # Create all database tables in the test SQLite database
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # Seed host
        host = Host(
            id="host_test",
            username="test_user",
            email="test@user.com",
            password_hash="mocked_hash"
        )
        db.add(host)
        
        # Seed property
        prop = Property(
            id="property_test_1",
            user_id="host_test",
            address="123 Main St",
            city="Miami",
            state="FL",
            zip_code="33139",
            property_type="Single-Family",
            zoning_status="Pending"
        )
        db.add(prop)
        
        # Seed municipal code
        mc = MunicipalCode(
            id=uuid.UUID("11111111-2222-3333-4444-55555555555f"),
            municipality_name="Miami",
            ordinance_number="MIA-ZONING-1",
            str_prohibited=True,
            jurisdiction_type="City",
            requires_permit=True,
            permit_name="Florida DBPR License task"
        )


        db.add(mc)
        
        # Seed checklist item (PropertyCompliance)
        checklist_item = PropertyCompliance(
            id=uuid.UUID("abcdef12-3456-7890-abcd-ef1234567890"),
            property_id="property_test_1",
            municipal_code_id=uuid.UUID("11111111-2222-3333-4444-55555555555f"),
            is_compliant=False,
            status="PENDING",
            violation_notes="Florida DBPR License task",
            valid_period="[2026-06-04 00:00:00, 2027-06-04 00:00:00]"
        )
        db.add(checklist_item)

        # Seed Ordinances
        from app.db_models import Ordinance
        ord1 = Ordinance(
            id=1,
            jurisdiction="Miami",
            ordinance_text="Noise control and short term rentals rules in Miami city.",
            embedding=[0.1] * 1536
        )
        ord2 = Ordinance(
            id=2,
            jurisdiction="Orlando",
            ordinance_text="Registration requirement for rentals.",
            embedding=[0.2] * 1536
        )
        db.add(ord1)
        db.add(ord2)
        db.commit()

    finally:
        db.close()

    yield
    # Clean up after all tests are done
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_compliance_endpoint.db"):
        os.remove("test_compliance_endpoint.db")

client = TestClient(fastapi_app)

def test_get_compliance_missing_address():
    """
    Test that calling GET /api/v1/compliance without the address parameter
    returns a 400 Bad Request or 422 Unprocessable Entity.
    """
    response = client.get("/api/v1/compliance")
    assert response.status_code in [400, 422]

def test_get_compliance_by_address_success():
    """
    Test that calling GET /api/v1/compliance?address=123+Main+St
    returns the compliance checklist items for the property, querying
    municipal_codes and property_compliance tables.
    """
    response = client.get("/api/v1/compliance", params={"address": "123 Main St"})
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "123 Main St"
    assert data["is_compliant"] is False
    assert "checklist" in data
    assert len(data["checklist"]) == 1
    assert data["checklist"][0]["task_name"] == "Florida DBPR License task"
    assert data["checklist"][0]["status"] == "PENDING"
    assert data["checklist"][0]["is_compliant"] is False

def test_get_compliance_by_address_not_found():
    """
    Test that calling GET /api/v1/compliance?address=999+Unknown+St
    returns 404 Not Found.
    """
    response = client.get("/api/v1/compliance", params={"address": "999 Unknown St"})
    assert response.status_code == 404

def test_search_compliance_missing_query():
    """
    Test that calling GET /api/v1/compliance/search without query returns 422/400.
    """
    response = client.get("/api/v1/compliance/search")
    assert response.status_code in [400, 422]

def test_search_compliance_success():
    """
    Test successful search lookup. Under SQLite, it should fall back to standard text search.
    """
    response = client.get("/api/v1/compliance/search", params={"query": "Noise control"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["jurisdiction"] == "Miami"
    assert "Noise control" in data[0]["ordinance_text"]

def test_search_compliance_fallback_on_exception():
    """
    Test that search fallback works when we force pgvector/database query failures.
    """
    with patch("app.api.v1.compliance.generate_embedding") as mock_embed:
        mock_embed.side_effect = Exception("Service unavailable")
        response = client.get("/api/v1/compliance/search", params={"query": "Registration"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["jurisdiction"] == "Orlando"

