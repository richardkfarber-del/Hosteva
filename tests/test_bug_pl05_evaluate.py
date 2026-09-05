"""BUG-PL-05: POST /api/properties/{id}/evaluate must not claim Compliant for Restricted / checklist."""
import os
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_bug_pl05_evaluate.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_bug_pl05_evaluate.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-pl05-evaluate")

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.models.compliance import MunicipalCode
from app.core.security import get_current_user, get_password_hash
from app.routers.properties import _map_compliance_label_to_zoning
from app.schemas.compliance import AddressComplianceResponse

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    host = Host(
        id="host_pl05",
        username="pl05_host",
        email="pl05@host.test",
        password_hash=get_password_hash("x"),
    )
    db.add(host)
    db.add(MunicipalCode(
        id=uuid.uuid4(),
        municipality_name="Miami Beach",
        ordinance_number="MB-STR-PROHIBITION",
        jurisdiction_type="City",
        state="FL",
        is_allowed=False,
        str_prohibited=True,
        requires_permit=True,
        is_ai_scraped=False,
        is_expert_verified=True,
    ))
    db.add(MunicipalCode(
        id=uuid.uuid4(),
        municipality_name="Spring Hill",
        ordinance_number="SH-TEST",
        jurisdiction_type="City",
        state="FL",
        is_allowed=True,
        str_prohibited=False,
        requires_permit=True,
        is_ai_scraped=False,
        is_expert_verified=True,
    ))
    # MB property (RESTRICTED truth)
    db.add(Property(
        id="prop_mb_pl05",
        user_id="host_pl05",
        address="1700 Convention Center Dr",
        city="Miami Beach",
        state="FL",
        zip_code="33139",
        property_type="Single Family",
        zoning_status="Violation",
    ))
    # Stable Run (ALLOWED_WITH_CHECKLIST)
    db.add(Property(
        id="prop_stable_pl05",
        user_id="host_pl05",
        address="15758 Stable Run Drive",
        city="Spring Hill",
        state="FL",
        zip_code="34610",
        property_type="Single Family",
        zoning_status="Pending",
    ))
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    prev_db = app.dependency_overrides.get(get_db)
    prev_user = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: {"username": "pl05_host", "role": "host"}
    yield
    app.dependency_overrides.pop(get_current_user, None)
    if prev_db is not None:
        app.dependency_overrides[get_db] = prev_db
    else:
        app.dependency_overrides.pop(get_db, None)
    if prev_user is not None:
        app.dependency_overrides[get_current_user] = prev_user
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_map_never_compliant_for_restricted_or_checklist():
    assert _map_compliance_label_to_zoning("RESTRICTED") == "Violation"
    assert _map_compliance_label_to_zoning("UNDER_REVIEW") == "Pending"
    assert _map_compliance_label_to_zoning("ALLOWED_WITH_CHECKLIST") == "Action Required"
    assert _map_compliance_label_to_zoning("COMPLIANT") != "Compliant"


def test_evaluate_mb_restricted_not_compliant():
    fake = AddressComplianceResponse(
        address="1700 Convention Center Dr, Miami Beach, FL 33139",
        is_compliant=False,
        is_under_review=False,
        status="RESTRICTED",
        municipal_code=None,
        hoa_rule=None,
        checklist=[],
    )
    with patch("app.api.v1.compliance.get_compliance_by_address", return_value=fake):
        r = client.post("/api/properties/prop_mb_pl05/evaluate")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] != "Compliant"
    assert data["status"] == "Violation"
    assert data.get("compliance_status") == "RESTRICTED"


def test_evaluate_stable_run_checklist_not_compliant():
    fake = AddressComplianceResponse(
        address="15758 Stable Run Drive, Spring Hill, FL 34610",
        is_compliant=True,
        is_under_review=False,
        status="ALLOWED_WITH_CHECKLIST",
        municipal_code=None,
        hoa_rule=None,
        checklist=[],
    )
    with patch("app.api.v1.compliance.get_compliance_by_address", return_value=fake):
        r = client.post("/api/properties/prop_stable_pl05/evaluate")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] != "Compliant"
    assert data["status"] == "Action Required"
    assert data.get("compliance_status") == "ALLOWED_WITH_CHECKLIST"


def test_evaluate_persists_non_compliant_zoning():
    fake = AddressComplianceResponse(
        address="x",
        is_compliant=False,
        is_under_review=False,
        status="RESTRICTED",
        municipal_code=None,
        hoa_rule=None,
        checklist=[],
    )
    with patch("app.api.v1.compliance.get_compliance_by_address", return_value=fake):
        client.post("/api/properties/prop_mb_pl05/evaluate")
    db = TestingSessionLocal()
    try:
        prop = db.query(Property).filter(Property.id == "prop_mb_pl05").first()
        assert prop.zoning_status == "Violation"
        assert prop.zoning_status != "Compliant"
    finally:
        db.close()
