import pytest
import uuid
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Force SQLite test URL globally
os.environ["DATABASE_URL"] = "sqlite:///./test_audit_v1.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_audit_v1.db"

from app.database import Base
from app.models.host import Host
from app.models.property import Property
from app.models.compliance import MunicipalCode, PropertyCompliance
from app.tasks.audit import process_document_ocr
from app.tasks.config import celery_app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_audit_v1.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def bind_session_local():
    from app.database import SessionLocal
    SessionLocal.configure(bind=engine)
    yield


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed host
        host = Host(
            id="host_audit_test",
            username="audit_host",
            email="audit@hosteva.com",
            password_hash="mocked_hash"
        )
        db.add(host)
        
        # Seed property
        prop = Property(
            id="property_audit_test",
            user_id="host_audit_test",
            address="789 Collins Ave",
            city="Miami Beach",
            state="FL",
            zip_code="33139",
            property_type="Apartment"
        )
        db.add(prop)
        
        # Seed municipal code
        mc = MunicipalCode(
            id=uuid.UUID("33333333-4444-5555-6666-77777777777f"),
            municipality_name="Miami Beach",
            ordinance_number="MB-STR-2",
            requires_permit=True
        )
        db.add(mc)
        
        # Seed compliance task
        task = PropertyCompliance(
            id=uuid.UUID("abcdef12-9999-8888-7777-666666666666"),
            property_id="property_audit_test",
            municipal_code_id=uuid.UUID("33333333-4444-5555-6666-77777777777f"),
            is_compliant=False,
            status="PENDING",
            task_name="STR Permit Application",
            valid_period="[2026-06-04 00:00:00, 2027-06-04 00:00:00]"
        )
        db.add(task)
        
        db.commit()
    finally:
        db.close()
        
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_audit_v1.db"):
        os.remove("test_audit_v1.db")

def test_process_document_ocr_success():
    """
    Test successful background OCR audit.
    Task should parse mock Gemini output, match owner/address, and mark compliance task as APPROVED.
    """
    mock_gemini_response = {
        "owner_name": "audit_host",
        "site_address": "789 Collins Ave",
        "license_number": "LIC-999234",
        "expiration_date": "2030-12-31",
        "is_valid": True,
        "verification_notes": "Perfect matching details."
    }
    
    with patch("app.tasks.audit.call_gemini_ocr") as mock_gemini:
        mock_gemini.return_value = mock_gemini_response
        
        # Run Celery task synchronously
        task_id = "abcdef12-9999-8888-7777-666666666666"
        res = process_document_ocr.delay(task_id, "s3://hosteva-documents/dummy.pdf")
        assert res.get() is True
        
        # Query DB to check updates
        db = TestingSessionLocal()
        item = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid.UUID(task_id)).first()
        assert item.status == "APPROVED"
        assert item.is_compliant is True
        assert item.uploaded_file_url == "s3://hosteva-documents/dummy.pdf"
        
        meta = json.loads(item.ocr_metadata_json)
        assert meta["owner_name"] == "audit_host"
        assert meta["license_number"] == "LIC-999234"
        db.close()

def test_process_document_ocr_pending_review_mismatch():
    """
    Test fallback review queue (PENDING_REVIEW) on document mismatches.
    Task should capture the mismatched field and raw OCR data in DB.
    """
    mock_gemini_response = {
        "owner_name": "audit_host",
        "site_address": "999 Mismatch Rd",  # Address mismatch
        "license_number": "LIC-999234",
        "expiration_date": "2030-12-31",
        "is_valid": True,
        "verification_notes": "Mismatched address."
    }
    
    # Update checklist item back to PENDING
    db = TestingSessionLocal()
    task_id = "abcdef12-9999-8888-7777-666666666666"
    item = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid.UUID(task_id)).first()
    item.status = "PENDING"
    item.is_compliant = False
    db.commit()
    db.close()
    
    with patch("app.tasks.audit.call_gemini_ocr") as mock_gemini:
        mock_gemini.return_value = mock_gemini_response
        
        res = process_document_ocr.delay(task_id, "s3://hosteva-documents/dummy.pdf")
        assert res.get() is True
        
        db = TestingSessionLocal()
        item = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid.UUID(task_id)).first()
        # Should be routed to PENDING_REVIEW instead of REJECTED (coworker resolution)
        assert item.status == "PENDING_REVIEW"
        assert item.is_compliant is False
        assert "Address Mismatch" in item.verification_notes
        assert item.ocr_metadata_json is not None
        db.close()
