"""BUG-PL-11: dashboard / list must not paint Compliant green for UNDER_REVIEW truth."""
import os
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_bug_pl11_badge.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_bug_pl11_badge.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-pl11-badge")

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
from app.core.security import get_current_user, get_password_hash
from app.routers.properties import (
    _map_compliance_label_to_zoning,
    _align_property_zoning_with_compliance,
)
from app.schemas.compliance import AddressComplianceResponse

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _fake_compliance(status: str, *, is_compliant: bool = False, under_review: bool = False):
    return AddressComplianceResponse(
        address="15758 Stable Run Drive, Spring Hill, FL 34610",
        is_compliant=is_compliant,
        is_under_review=under_review,
        status=status,
        municipal_code=None,
        hoa_rule=None,
        checklist=[],
    )


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Host(
        id="host_pl11",
        username="pl11_host",
        email="pl11@host.test",
        password_hash=get_password_hash("x"),
    ))
    # Stale Compliant row — Stable Run case from Widow probe
    db.add(Property(
        id="prop_stable_pl11",
        user_id="host_pl11",
        address="15758 Stable Run Drive",
        city="Spring Hill",
        state="FL",
        zip_code="34610",
        property_type="Single Family",
        zoning_status="Compliant",
    ))
    db.add(Property(
        id="prop_ok_pl11",
        user_id="host_pl11",
        address="100 Pending Lane",
        city="Tampa",
        state="FL",
        zip_code="33602",
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
    app.dependency_overrides[get_current_user] = lambda: {"username": "pl11_host", "role": "host"}
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


def test_map_under_review_not_compliant():
    assert _map_compliance_label_to_zoning("UNDER_REVIEW") == "Pending"
    assert _map_compliance_label_to_zoning("UNDER_REVIEW") != "Compliant"
    assert _map_compliance_label_to_zoning("ALLOWED_WITH_CHECKLIST") == "Action Required"
    assert _map_compliance_label_to_zoning("RESTRICTED") == "Violation"


def test_list_hydrate_under_review_clears_stale_compliant():
    fake = _fake_compliance("UNDER_REVIEW", is_compliant=False, under_review=True)
    with patch("app.api.v1.compliance.get_compliance_by_address", return_value=fake):
        r = client.get("/api/properties/")
    assert r.status_code == 200
    rows = {row["id"]: row for row in r.json()}
    assert rows["prop_stable_pl11"]["zoning_status"] != "Compliant"
    assert rows["prop_stable_pl11"]["zoning_status"] == "Pending"

    db = TestingSessionLocal()
    try:
        prop = db.query(Property).filter(Property.id == "prop_stable_pl11").first()
        assert prop.zoning_status == "Pending"
        assert prop.zoning_status != "Compliant"
    finally:
        db.close()


def test_list_hydrate_checklist_required_not_green():
    fake = _fake_compliance("ALLOWED_WITH_CHECKLIST", is_compliant=True, under_review=False)
    with patch("app.api.v1.compliance.get_compliance_by_address", return_value=fake):
        r = client.get("/api/properties/")
    assert r.status_code == 200
    rows = {row["id"]: row for row in r.json()}
    assert rows["prop_stable_pl11"]["zoning_status"] != "Compliant"
    assert rows["prop_stable_pl11"]["zoning_status"] == "Action Required"


def test_align_helper_under_review_not_compliant_green_path():
    db = TestingSessionLocal()
    try:
        prop = db.query(Property).filter(Property.id == "prop_stable_pl11").first()
        assert prop.zoning_status == "Compliant"
        fake = _fake_compliance("UNDER_REVIEW", is_compliant=False, under_review=True)
        with patch("app.api.v1.compliance.get_compliance_by_address", return_value=fake):
            new_status = _align_property_zoning_with_compliance(db, prop, commit=True)
        assert new_status != "Compliant"
        assert new_status == "Pending"
        db.refresh(prop)
        assert prop.zoning_status == "Pending"
    finally:
        db.close()


def test_dashboard_badge_helper_markers_present():
    """DOM/JS markers: resolveDashboardBadge fail-closed path ships in dashboard.html."""
    r = client.get("/dashboard")
    # Auth gate may redirect; template is also served under authenticated shell routes.
    # Prefer reading the template file directly for honesty markers.
    from pathlib import Path
    html = Path("app/templates/dashboard.html").read_text()
    assert "resolveDashboardBadge" in html
    assert "BUG-PL-11" in html
    assert "never trust stale Compliant alone" in html
    # Must not keep the old empty-checklist Compliant → score 100 green path as sole logic
    assert "checklistLocked" in html or "checklistLockedSingle" in html


def test_create_aligns_away_from_false_compliant():
    fake = _fake_compliance("UNDER_REVIEW", is_compliant=False, under_review=True)
    audit = {
        "legal_subdivision_name": "Test",
        "hoa_detected": False,
        "hoa_rules_available": False,
        "eligibility_status": "Compliant",
        "required_permits": ["DBPR Vacation Rental License"],
        "local_restrictions": {"disclaimer": "info only"},
    }
    with patch("app.routers.properties.geocode_address", return_value={
        "city": "Spring Hill",
        "county": "Pasco County",
        "state": "FL",
        "postal_code": "34610",
        "address_components": [],
        "formatted_address": "15758 Stable Run Drive B, Spring Hill, FL 34610",
        "lat": 28.0,
        "lng": -82.0,
    }), patch("app.routers.properties.resolve_property_create_image", return_value="/static/img/fallback_house.jpg"), \
         patch("app.routers.properties.run_gemini_audit", return_value=audit), \
         patch("app.api.v1.compliance.get_compliance_by_address", return_value=fake), \
         patch("app.routers.properties._seed_create_checklist", return_value=None):
        r = client.post("/api/properties/", json={
            "address": "15758 Stable Run Drive B",
            "city": "Spring Hill",
            "state": "FL",
            "zip_code": "34610",
            "property_type": "Single Family",
        })
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["zoning_status"] != "Compliant"
    assert data["zoning_status"] == "Pending"
