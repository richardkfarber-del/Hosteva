import pytest
import uuid
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite:///./test_hoa_upload.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_hoa_upload.db"

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.models.compliance import PropertyCompliance, HOARule, MunicipalCode

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_hoa_upload.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def bind_session_local():
    from app.database import SessionLocal
    SessionLocal.configure(bind=engine)
    yield

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        host = Host(
            id="hoa_test_host",
            username="hoa_user",
            email="hoa@test.com",
            password_hash="mocked_hash"
        )
        db.add(host)

        prop = Property(
            id="hoa_test_property",
            user_id="hoa_test_host",
            address="100 Ocean Drive",
            city="Miami Beach",
            state="FL",
            zip_code="33139",
            property_type="Condo",
            zoning_status="Awaiting Audit"
        )
        db.add(prop)

        mc = MunicipalCode(
            id=uuid.UUID("33333333-4444-5555-6666-77777777777f"),
            municipality_name="Miami Beach",
            ordinance_number="MB-HOA-1",
            requires_permit=True
        )
        db.add(mc)

        task = PropertyCompliance(
            id=uuid.UUID("11111111-2222-3333-4444-555555555555"),
            property_id="hoa_test_property",
            municipal_code_id=mc.id,
            is_compliant=False,
            status="PENDING",
            task_name="HOA Registration & Document Verification",
            valid_period="[2026-06-04 00:00:00, 2027-06-04 00:00:00]"
        )
        db.add(task)

        db.commit()
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_hoa_upload.db"):
        os.remove("test_hoa_upload.db")


def test_hoa_document_upload_success():
    client = TestClient(app)
    mock_response = {
        "hoa_name": "Ocean Drive Condo Association",
        "str_permitted": "Yes",
        "minimum_lease_stay": "None",
        "key_rules_notes": "Short-term rentals permitted with annual registration.",
        "is_valid": True
    }

    with patch("app.api.v1.compliance.call_gemini_hoa_ocr", return_value=mock_response):
        dummy_file = ("hoa_bylaws.txt", b"HOA bylaws text: short term rentals allowed", "text/plain")
        response = client.post(
            "/api/v1/compliance/hoa/upload",
            data={"property_id": "hoa_test_property"},
            files={"file": dummy_file}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "APPROVED"
        assert data["hoa_name"] == "Ocean Drive Condo Association"
        assert data["str_permitted"] == "Yes"
        assert "compliance_score" in data
        assert data["compliance_score"] == 100.0
        assert "/api/v1/compliance/documents/" in data["uploaded_file_url"]

        db = TestingSessionLocal()
        prop = db.query(Property).filter(Property.id == "hoa_test_property").first()
        assert prop.zoning_status == "Compliant"
        assert prop.hoa_status is True

        task = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid.UUID("11111111-2222-3333-4444-555555555555")).first()
        assert task.status == "APPROVED"
        assert task.is_compliant is True
        db.close()

