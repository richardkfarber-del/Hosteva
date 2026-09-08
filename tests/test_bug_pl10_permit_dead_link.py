"""BUG-PL-10: Permit generate must not 500 on beds/bedrooms; honest N/A + no dead #."""
import os
import uuid
import json

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_bug_pl10_permit.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_bug_pl10_permit.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-pl10-permit")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.core.security import get_current_user, get_password_hash
from app.services.permit_generator import (
    PermitGeneratorService,
    PermitNotApplicableError,
)

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
    db.add(Host(
        id="host_pl10",
        username="pl10_host",
        email="pl10@host.test",
        password_hash=get_password_hash("x"),
    ))
    # Compliant Stable Run-style property — API exposes beds; model has neither beds nor bedrooms
    db.add(Property(
        id="prop_compliant_pl10",
        user_id="host_pl10",
        address="12345 Stable Run Dr",
        city="Spring Hill",
        state="FL",
        zip_code="34610",
        property_type="Single Family",
        zoning_status="Compliant",
        required_permits=json.dumps(["Pasco County STR Permit"]),
        local_restrictions=json.dumps({"requires_permit": True}),
    ))
    db.add(Property(
        id="prop_under_review_pl10",
        user_id="host_pl10",
        address="999 Research Lane",
        city="Ocala",
        state="FL",
        zip_code="34471",
        property_type="Single Family",
        zoning_status="Under Review",
        required_permits=json.dumps([]),
        local_restrictions=json.dumps({}),
    ))
    db.add(Property(
        id="prop_no_permit_pl10",
        user_id="host_pl10",
        address="1 No Permit Way",
        city="Example",
        state="FL",
        zip_code="32000",
        property_type="Single Family",
        zoning_status="Compliant",
        required_permits=json.dumps([]),
        local_restrictions=json.dumps({
            "requires_permit": False,
            "permit_status": "No permit required",
        }),
    ))
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_user():
        return {"id": "host_pl10", "sub": "host_pl10", "email": "pl10@host.test"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_bed_count_prefers_beds_over_bedrooms():
    class Fake:
        beds = 4
        bedrooms = 9

    assert PermitGeneratorService._bed_count(Fake()) == 4


def test_bed_count_falls_back_when_model_has_neither():
    class Bare:
        pass

    assert PermitGeneratorService._bed_count(Bare()) == 2


def test_bed_count_uses_bedrooms_if_only_legacy_attr():
    class Legacy:
        bedrooms = 5

    assert PermitGeneratorService._bed_count(Legacy()) == 5


def test_generate_compliant_no_500_uses_beds_semantics():
    """Core PL-10: AttributeError bedrooms must not 500; generate succeeds."""
    assert not hasattr(Property, "bedrooms")
    assert not hasattr(Property, "beds")

    resp = client.post(
        "/api/permit-generator/generate",
        json={"property_id": "prop_compliant_pl10"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["application_id"].startswith("APP-")
    assert data["property_id"] == "prop_compliant_pl10"
    assert data["county"] in ("Pasco", "Hillsborough")
    assert isinstance(data["required_documents"], list) and len(data["required_documents"]) > 0
    assert "bedrooms" not in (resp.text.lower().split("attribute")[0] if "attribute" in resp.text.lower() else "")
    assert data.get("beds_used") == 2  # default when model has no beds column
    # Real openable URL — not dead #
    url = data.get("download_url") or data.get("application_url")
    assert url and url != "#"
    assert url.startswith("/static/generated_permits/")


def test_generate_does_not_mention_bedrooms_attribute_error():
    resp = client.post(
        "/api/permit-generator/generate",
        json={"property_id": "prop_compliant_pl10"},
    )
    assert resp.status_code != 500
    assert "has no attribute 'bedrooms'" not in resp.text


def test_under_review_returns_422_not_500():
    resp = client.post(
        "/api/permit-generator/generate",
        json={"property_id": "prop_under_review_pl10"},
    )
    assert resp.status_code == 422, resp.text
    assert "under review" in resp.json()["detail"].lower() or "pending" in resp.json()["detail"].lower()


def test_no_permit_jurisdiction_returns_422():
    resp = client.post(
        "/api/permit-generator/generate",
        json={"property_id": "prop_no_permit_pl10"},
    )
    assert resp.status_code == 422, resp.text
    assert "not applicable" in resp.json()["detail"].lower() or "not required" in resp.json()["detail"].lower()


def test_missing_property_404():
    resp = client.post(
        "/api/permit-generator/generate",
        json={"property_id": "does-not-exist"},
    )
    assert resp.status_code == 404


def test_service_applicability_helpers():
    db = TestingSessionLocal()
    ur = db.query(Property).filter(Property.id == "prop_under_review_pl10").one()
    ok, reason = PermitGeneratorService.permit_applicability(ur)
    assert ok is False and reason

    good = db.query(Property).filter(Property.id == "prop_compliant_pl10").one()
    ok2, reason2 = PermitGeneratorService.permit_applicability(good)
    assert ok2 is True and reason2 is None
    db.close()


def test_dashboard_dom_permit_honesty_markers():
    """UI: no dead href=# on permit-link; N/A + inline error helpers present.

    /dashboard requires auth cookie and redirects to login — assert the template
    source directly (same pattern as US-015 CTA DOM tests).
    """
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] / "app" / "templates" / "dashboard.html").read_text()
    assert 'id="permit-link"' in html
    # Default must not be a clickable dead #
    assert 'id="permit-link" href="#"' not in html
    assert 'href=""' in html or 'id="permit-link" href=""' in html or "removeAttribute('href')" in html
    assert "isPermitNotApplicable" in html
    assert "permit-inline-error" in html
    assert "Permit N/A" in html
    assert "BUG-PL-10" in html
    assert "never leave a clickable dead href" in html or "do not leave a clickable dead PERMIT" in html
