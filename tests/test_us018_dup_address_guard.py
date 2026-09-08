"""US-018 — Host-scoped duplicate address guard.

Same host cannot double-add; friendly Wasp copy on 409; other hosts unblocked.
No Option B / CTA / Street View / Pasco / US-018b cleanup in this change.
"""
import os
import uuid
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_us018_dup.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_us018_dup.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-us018-dup")

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
from app.services.duplicate_address import (
    DUP_ACTION_LABEL,
    DUP_BANNER_BODY,
    DUP_BANNER_TITLE,
    DUP_CODE,
    DUP_INLINE,
    addresses_equivalent,
    find_host_duplicate_property,
    normalize_part,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = (REPO_ROOT / "app" / "templates" / "dashboard.html").read_text()
WIZARD_JS = (REPO_ROOT / "app" / "static" / "js" / "wizard.js").read_text()

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

HOST_A = "host_us018_a"
HOST_B = "host_us018_b"
USER_A = "us018_host_a"
USER_B = "us018_host_b"

ADDR = {
    "address": "123 Palm Ave",
    "city": "Tampa",
    "state": "FL",
    "zip_code": "33602",
    "property_type": "Single Family",
}


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Host(id=HOST_A, username=USER_A, email="a@us018.test", password_hash=get_password_hash("x")))
    db.add(Host(id=HOST_B, username=USER_B, email="b@us018.test", password_hash=get_password_hash("x")))
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
    app.dependency_overrides[get_current_user] = lambda: {"username": USER_A, "role": "host"}
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


def _as_user(username: str):
    app.dependency_overrides[get_current_user] = lambda: {"username": username, "role": "host"}


def _v1_payload(address=None, city=None, state=None, zip_code=None):
    return {
        "address": {
            "address": address if address is not None else ADDR["address"],
            "city": city if city is not None else ADDR["city"],
            "state": state if state is not None else ADDR["state"],
            "zip_code": zip_code if zip_code is not None else ADDR["zip_code"],
        },
        "property_type": ADDR["property_type"],
        "compliance_data": {
            "zoning_status": "Pending",
            "hoa_status": False,
            "required_permits": [],
            "local_restrictions": {},
        },
    }


def _legacy_payload(**overrides):
    body = {
        "address": ADDR["address"],
        "city": ADDR["city"],
        "state": ADDR["state"],
        "zip_code": ADDR["zip_code"],
        "property_type": ADDR["property_type"],
    }
    body.update(overrides)
    return body


def _seed_property(host_id, address=None, city=None, state=None, zip_code=None):
    db = TestingSessionLocal()
    try:
        prop = Property(
            id=str(uuid.uuid4()),
            user_id=host_id,
            address=address if address is not None else ADDR["address"],
            city=city if city is not None else ADDR["city"],
            state=state if state is not None else ADDR["state"],
            zip_code=zip_code if zip_code is not None else ADDR["zip_code"],
            property_type="Single Family",
            zoning_status="Pending",
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)
        return prop.id
    finally:
        db.close()


def _count_host_props(host_id):
    db = TestingSessionLocal()
    try:
        return db.query(Property).filter(Property.user_id == host_id).count()
    finally:
        db.close()


# --- unit: normalize / match ---


def test_normalize_trim_case():
    assert normalize_part("  123 Palm Ave  ") == "123 palm ave"
    assert addresses_equivalent(
        "123 Palm Ave", "Tampa", "FL", "33602",
        "123 palm ave", "tampa", "fl", "33602",
    )
    assert addresses_equivalent(
        "  123   Palm Ave ", "Tampa", "Florida", "",
        "123 Palm Ave", "Tampa", "FL", "33602",
    )


def test_find_host_duplicate_scoped():
    existing_id = _seed_property(HOST_A)
    db = TestingSessionLocal()
    try:
        hit = find_host_duplicate_property(db, HOST_A, "123 palm ave", "TAMPA", "fl", "33602")
        assert hit is not None and hit.id == existing_id
        miss = find_host_duplicate_property(db, HOST_B, "123 Palm Ave", "Tampa", "FL", "33602")
        assert miss is None
    finally:
        db.close()


# --- API: /api/v1/properties ---


@patch("app.routers.properties.geocode_address", return_value={"city": "Tampa", "county": "Hillsborough County", "state": "FL"})
@patch("app.routers.properties.resolve_property_create_image", return_value="/static/img/fallback_house.jpg")
def test_v1_exact_duplicate_blocked_with_wasp_copy(mock_img, mock_geo):
    existing_id = _seed_property(HOST_A)
    before = _count_host_props(HOST_A)
    _as_user(USER_A)
    res = client.post("/api/v1/properties/", json=_v1_payload())
    assert res.status_code == 409
    detail = res.json()["detail"]
    assert detail["code"] == DUP_CODE
    assert detail["title"] == DUP_BANNER_TITLE
    assert detail["message"] == DUP_BANNER_BODY
    assert detail["action_label"] == DUP_ACTION_LABEL
    assert detail["inline"] == DUP_INLINE
    assert detail["existing_property_id"] == existing_id
    assert detail["existing_property_url"] == f"/manage/{existing_id}"
    assert "409" not in detail["title"]
    assert "duplicate key" not in detail["message"].lower()
    assert "forbidden" not in detail["message"].lower()
    assert _count_host_props(HOST_A) == before


@patch("app.routers.properties.geocode_address", return_value={"city": "Tampa", "county": "Hillsborough County", "state": "FL"})
@patch("app.routers.properties.resolve_property_create_image", return_value="/static/img/fallback_house.jpg")
def test_v1_normalized_variant_blocked(mock_img, mock_geo):
    _seed_property(HOST_A)
    before = _count_host_props(HOST_A)
    _as_user(USER_A)
    res = client.post(
        "/api/v1/properties/",
        json=_v1_payload(address="  123 PALM AVE ", city="tampa", state="florida", zip_code="33602"),
    )
    assert res.status_code == 409
    assert res.json()["detail"]["title"] == DUP_BANNER_TITLE
    assert _count_host_props(HOST_A) == before


@patch("app.routers.properties.geocode_address", return_value={"city": "Tampa", "county": "Hillsborough County", "state": "FL"})
@patch("app.routers.properties.resolve_property_create_image", return_value="/static/img/fallback_house.jpg")
def test_v1_other_host_may_save_same_address(mock_img, mock_geo):
    _seed_property(HOST_A)
    _as_user(USER_B)
    res = client.post("/api/v1/properties/", json=_v1_payload())
    assert res.status_code == 201, res.text
    assert _count_host_props(HOST_A) == 1
    assert _count_host_props(HOST_B) == 1


@patch("app.routers.properties.geocode_address", return_value={"city": "Tampa", "county": "Hillsborough County", "state": "FL"})
@patch("app.routers.properties.resolve_property_create_image", return_value="/static/img/fallback_house.jpg")
def test_v1_first_create_still_succeeds(mock_img, mock_geo):
    _as_user(USER_A)
    res = client.post("/api/v1/properties/", json=_v1_payload(address="999 New St"))
    assert res.status_code == 201, res.text
    assert _count_host_props(HOST_A) == 1


# --- API: /api/properties/ (legacy / pending handoff) ---


@patch("app.routers.properties.geocode_address", return_value={"city": "Tampa", "county": "Hillsborough County", "state": "FL"})
@patch("app.routers.properties.resolve_property_create_image", return_value="/static/img/fallback_house.jpg")
@patch("app.routers.properties.run_gemini_audit")
def test_legacy_duplicate_blocked(mock_audit, mock_img, mock_geo):
    mock_audit.return_value = {
        "hoa_detected": False,
        "eligibility_status": "Pending",
        "required_permits": [],
        "local_restrictions": {},
    }
    existing_id = _seed_property(HOST_A)
    before = _count_host_props(HOST_A)
    _as_user(USER_A)
    res = client.post("/api/properties/", json=_legacy_payload())
    assert res.status_code == 409
    detail = res.json()["detail"]
    assert detail["existing_property_id"] == existing_id
    assert detail["title"] == DUP_BANNER_TITLE
    assert _count_host_props(HOST_A) == before


# --- DOM / copy wiring ---


def test_dashboard_and_wizard_wasp_copy_and_action():
    for blob in (DASHBOARD, WIZARD_JS):
        assert DUP_BANNER_TITLE in blob
        assert DUP_BANNER_BODY in blob
        assert DUP_ACTION_LABEL in blob
        assert DUP_INLINE in blob
        assert "DUPLICATE_ADDRESS" in blob or "dup-address-banner" in blob
    assert 'id="dup-address-banner"' in DASHBOARD
    assert 'id="dup-address-open-existing"' in DASHBOARD
    assert "showDuplicateAddressBanner" in WIZARD_JS
    assert "existing_property_url" in WIZARD_JS
    # Must not surface engineer jargon as the primary message
    assert "Duplicate key" not in DASHBOARD
    assert "Error 409" not in DASHBOARD


def test_us018_out_of_scope_surfaces_untouched():
    """No Option B / CTA / Street View / Pasco allowlist edits in this PR's UI files."""
    assert "OPTION_B" not in DASHBOARD
    assert "Create a free account to see your checklist" not in DASHBOARD
    curated = (REPO_ROOT / "app" / "services" / "curated_coverage.py").read_text()
    # Guard file exists and was not the vehicle for this story
    assert "CURATED" in curated or "curated" in curated
    assert "duplicate_address" not in curated
