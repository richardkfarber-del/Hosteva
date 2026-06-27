import os
import io
import pytest
from datetime import date, datetime, timedelta
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Force SQLite test URL globally for all tests BEFORE any app models/modules are imported
os.environ["DATABASE_URL"] = "sqlite:///./test_ai_compliance_auditor.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_ai_compliance_auditor.db"

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode, PropertyCompliance, Region
from app.models.property import Property
from app.models.host import Host
import app.db_models

SQLAlchemy_DATABASE_URL = "sqlite:///./test_ai_compliance_auditor.db"
engine = create_engine(SQLAlchemy_DATABASE_URL, connect_args={"check_same_thread": False})
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
    # Create all database tables in the test SQLite database
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # Seed host
        host = Host(
            id="host_1",
            username="test_owner",
            email="owner@test.com",
            password_hash="mocked_hash"
        )
        db.add(host)
        
        # Seed property
        prop = Property(
            id="property_1",
            user_id="host_1",
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
            municipality_name="State of Florida",
            ordinance_number="FL-LICENSE-TEST",
            str_prohibited=False
        )
        db.add(mc)
        
        # Seed checklist item (PropertyCompliance)
        checklist_item = PropertyCompliance(
            id=uuid.UUID("abcdef12-3456-7890-abcd-ef1234567890"),
            property_id="property_1",
            municipal_code_id=uuid.UUID("11111111-2222-3333-4444-55555555555f"),
            is_compliant=False,
            status="PENDING",
            violation_notes="Florida DBPR License task",
            valid_period="[2026-06-04 00:00:00, 2027-06-04 00:00:00]"
        )
        db.add(checklist_item)
        db.commit()
    finally:
        db.close()

    yield
    # Clean up after all tests are done
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_ai_compliance_auditor.db"):
        os.remove("test_ai_compliance_auditor.db")

client = TestClient(fastapi_app)

def test_audit_document_success():
    """
    Test successful compliance document verification.
    The document owner name, site address, and future expiration date match the property records.
    Status should update to 'APPROVED'.
    """
    future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
    doc_content = f"""
    Registrant Name: test_owner
    Site Address: 123 Main St, Miami, FL 33139
    Expiration Date: {future_date}
    License Number: LIC-100200
    """
    
    file_payload = {
        "file": ("license.txt", io.BytesIO(doc_content.encode("utf-8")), "text/plain")
    }
    data_payload = {
        "checklist_item_id": "abcdef12-3456-7890-abcd-ef1234567890"
    }
    
    response = client.post("/api/v1/compliance/audit-document", files=file_payload, data=data_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "APPROVED"
    assert res_data["is_compliant"] is True
    assert res_data["rejection_notes"] is None
    
    # Check DB status
    db = TestingSessionLocal()
    item = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid.UUID("abcdef12-3456-7890-abcd-ef1234567890")).first()
    assert item.status == "APPROVED"
    assert item.is_compliant is True
    assert item.rejection_notes is None
    db.close()

def test_audit_document_name_mismatch():
    """
    Test compliance document verification failure due to mismatched owner/registrant name.
    Status should update to 'REJECTED'.
    """
    future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
    doc_content = f"""
    Registrant Name: Wrong Owner Name
    Site Address: 123 Main St, Miami, FL 33139
    Expiration Date: {future_date}
    License Number: LIC-100200
    """
    
    file_payload = {
        "file": ("license.txt", io.BytesIO(doc_content.encode("utf-8")), "text/plain")
    }
    data_payload = {
        "checklist_item_id": "abcdef12-3456-7890-abcd-ef1234567890"
    }
    
    response = client.post("/api/v1/compliance/audit-document", files=file_payload, data=data_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "REJECTED"
    assert res_data["is_compliant"] is False
    assert "Mismatched Owner Name" in res_data["rejection_notes"]
    
    # Check DB status
    db = TestingSessionLocal()
    item = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid.UUID("abcdef12-3456-7890-abcd-ef1234567890")).first()
    assert item.status == "REJECTED"
    assert item.is_compliant is False
    assert "Mismatched Owner Name" in item.rejection_notes
    db.close()

def test_audit_document_address_mismatch():
    """
    Test compliance document verification failure due to mismatched site address.
    Status should update to 'REJECTED'.
    """
    future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
    doc_content = f"""
    Registrant Name: test_owner
    Site Address: 999 Mismatched Way, Miami, FL 33139
    Expiration Date: {future_date}
    License Number: LIC-100200
    """
    
    file_payload = {
        "file": ("license.txt", io.BytesIO(doc_content.encode("utf-8")), "text/plain")
    }
    data_payload = {
        "checklist_item_id": "abcdef12-3456-7890-abcd-ef1234567890"
    }
    
    response = client.post("/api/v1/compliance/audit-document", files=file_payload, data=data_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "REJECTED"
    assert res_data["is_compliant"] is False
    assert "Mismatched Address" in res_data["rejection_notes"]
    
    # Check DB status
    db = TestingSessionLocal()
    item = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid.UUID("abcdef12-3456-7890-abcd-ef1234567890")).first()
    assert item.status == "REJECTED"
    assert item.is_compliant is False
    assert "Mismatched Address" in item.rejection_notes
    db.close()

def test_audit_document_expired_date():
    """
    Test compliance document verification failure due to an expired document date.
    Status should update to 'REJECTED'.
    """
    past_date = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
    doc_content = f"""
    Registrant Name: test_owner
    Site Address: 123 Main St, Miami, FL 33139
    Expiration Date: {past_date}
    License Number: LIC-100200
    """
    
    file_payload = {
        "file": ("license.txt", io.BytesIO(doc_content.encode("utf-8")), "text/plain")
    }
    data_payload = {
        "checklist_item_id": "abcdef12-3456-7890-abcd-ef1234567890"
    }
    
    response = client.post("/api/v1/compliance/audit-document", files=file_payload, data=data_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "REJECTED"
    assert res_data["is_compliant"] is False
    assert "Expired Document" in res_data["rejection_notes"]
    
    # Check DB status
    db = TestingSessionLocal()
    item = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid.UUID("abcdef12-3456-7890-abcd-ef1234567890")).first()
    assert item.status == "REJECTED"
    assert item.is_compliant is False
    assert "Expired Document" in item.rejection_notes
    db.close()

def test_get_checklist_items():
    """
    Test GET /api/v1/compliance/checklist-items/{property_id} returns all compliance tasks.
    """
    response = client.get("/api/v1/compliance/checklist-items/property_1")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["property_id"] == "property_1"
    assert items[0]["id"] == "abcdef12-3456-7890-abcd-ef1234567890"
    assert items[0]["violation_notes"] == "Florida DBPR License task"
