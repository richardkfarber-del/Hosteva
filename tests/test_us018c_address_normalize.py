"""US-018c / TE-011 — Normalize short vs full address lines before match.

Shared helper equates street-only with street+city+state+ZIP forms.
Prevent + cleanup inherit via addresses_equivalent.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_us018c_dup.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_us018c_dup.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-us018c-dup")
ADMIN_KEY = "test-admin-us018c"
os.environ.setdefault("ADMIN_API_KEY", ADMIN_KEY)

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
    DUP_BANNER_TITLE,
    DUP_CODE,
    addresses_equivalent,
    canonicalize_address_parts,
    find_host_duplicate_property,
)
from app.services.duplicate_cleanup import cleanup_host_duplicates

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY = REPO_ROOT / "docs" / "06_qa" / "TEST_INVENTORY.md"
CHANGELOG = REPO_ROOT / "docs" / "05_build" / "CHANGELOG.md"

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

HOST_A = "host_us018c_a"
HOST_B = "host_us018c_b"
USER_A = "us018c_host_a"
USER_B = "us018c_host_b"

SHORT = "15758 Stable Run Drive"
FULL = "15758 Stable Run Drive, Spring Hill, FL 34610"
CITY = "Spring Hill"
STATE = "FL"
ZIP = "34610"
OTHER_STREET = "100 Oak Drive"


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Host(id=HOST_A, username=USER_A, email="a@us018c.test", password_hash=get_password_hash("x")))
    db.add(Host(id=HOST_B, username=USER_B, email="b@us018c.test", password_hash=get_password_hash("x")))
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


def _seed_property(host_id, address, city="", state="", zip_code="", created_at=None):
    db = TestingSessionLocal()
    try:
        prop = Property(
            id=str(uuid.uuid4()),
            user_id=host_id,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            property_type="Single Family",
            zoning_status="Pending",
        )
        if created_at is not None:
            prop.created_at = created_at
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


def _v1_payload(address, city="", state="", zip_code=""):
    return {
        "address": {
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
        },
        "property_type": "Single Family",
        "compliance_data": {
            "zoning_status": "Pending",
            "hoa_status": False,
            "required_permits": [],
            "local_restrictions": {},
        },
    }


# --- unit: normalize / match ---


def test_canonicalize_peels_stable_run_full_line():
    street, city, state, zip5 = canonicalize_address_parts(FULL, "", "", "")
    assert street == "15758 stable run drive"
    assert city == "spring hill"
    assert state == "fl"
    assert zip5 == "34610"


def test_short_equiv_full_stable_run_and_variants():
    assert addresses_equivalent(SHORT, "", "", "", FULL, "", "", "")
    assert addresses_equivalent(FULL, "", "", "", SHORT, "", "", "")
    assert addresses_equivalent(
        SHORT, CITY, STATE, ZIP,
        FULL, "", "", "",
    )
    assert addresses_equivalent(
        "  15758   STABLE RUN drive ", "", "", "",
        "15758 Stable Run Drive, Spring Hill, FL 34610", "", "", "",
    )
    assert addresses_equivalent(
        SHORT, "", "", "",
        "15758 Stable Run Drive, Spring Hill, FL 34610.", "", "", "",
    )
    # ZIP punctuation / +4 soft on base
    assert addresses_equivalent(
        SHORT, CITY, STATE, "34610",
        "15758 Stable Run Drive, Spring Hill, FL 34610-1234", "", "", "",
    )


def test_distinct_streets_same_city_zip_not_equivalent():
    assert not addresses_equivalent(
        OTHER_STREET, CITY, STATE, ZIP,
        SHORT, CITY, STATE, ZIP,
    )
    assert not addresses_equivalent(
        f"{OTHER_STREET}, {CITY}, {STATE} {ZIP}", "", "", "",
        FULL, "", "", "",
    )


# --- Prevent: short↔full → 409 ---


@patch(
    "app.routers.properties.geocode_address",
    return_value={"city": CITY, "county": "Pasco County", "state": STATE},
)
@patch(
    "app.routers.properties.resolve_property_create_image",
    return_value="/static/img/fallback_house.jpg",
)
def test_prevent_short_exists_full_create_409(mock_img, mock_geo):
    existing = _seed_property(HOST_A, SHORT)
    before = _count_host_props(HOST_A)
    _as_user(USER_A)
    res = client.post("/api/v1/properties/", json=_v1_payload(FULL))
    assert res.status_code == 409, res.text
    detail = res.json()["detail"]
    assert detail["code"] == DUP_CODE
    assert detail["title"] == DUP_BANNER_TITLE
    assert detail["existing_property_id"] == existing
    assert _count_host_props(HOST_A) == before


@patch(
    "app.routers.properties.geocode_address",
    return_value={"city": CITY, "county": "Pasco County", "state": STATE},
)
@patch(
    "app.routers.properties.resolve_property_create_image",
    return_value="/static/img/fallback_house.jpg",
)
def test_prevent_full_exists_short_create_409(mock_img, mock_geo):
    existing = _seed_property(HOST_A, FULL)
    before = _count_host_props(HOST_A)
    _as_user(USER_A)
    res = client.post("/api/v1/properties/", json=_v1_payload(SHORT, CITY, STATE, ZIP))
    assert res.status_code == 409, res.text
    assert res.json()["detail"]["existing_property_id"] == existing
    assert _count_host_props(HOST_A) == before


@patch(
    "app.routers.properties.geocode_address",
    return_value={"city": CITY, "county": "Pasco County", "state": STATE},
)
@patch(
    "app.routers.properties.resolve_property_create_image",
    return_value="/static/img/fallback_house.jpg",
)
def test_distinct_street_still_creatable(mock_img, mock_geo):
    _seed_property(HOST_A, SHORT, CITY, STATE, ZIP)
    _as_user(USER_A)
    res = client.post(
        "/api/v1/properties/",
        json=_v1_payload(OTHER_STREET, CITY, STATE, ZIP),
    )
    assert res.status_code == 201, res.text
    assert _count_host_props(HOST_A) == 2


# --- Cleanup: residual short+full → 1 canonical ---


def test_cleanup_residual_short_full_collapses_to_one():
    db = TestingSessionLocal()
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    early = Property(
        id="sr-short",
        user_id=HOST_A,
        address=SHORT,
        city="",
        state="",
        zip_code="",
        property_type="Single Family",
        zoning_status="Pending",
        created_at=t0,
    )
    late = Property(
        id="sr-full",
        user_id=HOST_A,
        address=FULL,
        city="",
        state="",
        zip_code="",
        property_type="Single Family",
        zoning_status="Pending",
        created_at=t0 + timedelta(days=1),
    )
    db.add_all([early, late])
    db.commit()

    result = cleanup_host_duplicates(db, HOST_A)
    db.commit()
    remaining = db.query(Property).filter(Property.user_id == HOST_A).all()
    assert len(remaining) == 1
    assert remaining[0].id == "sr-short"  # equal richness → earliest
    assert result.groups_merged == 1
    assert result.properties_removed == 1

    # Idempotent
    result2 = cleanup_host_duplicates(db, HOST_A)
    assert result2.groups_merged == 0
    assert result2.properties_removed == 0
    db.close()


def test_cleanup_does_not_merge_distinct_streets_same_city_zip():
    db = TestingSessionLocal()
    db.add(
        Property(
            id="oak",
            user_id=HOST_A,
            address=OTHER_STREET,
            city=CITY,
            state=STATE,
            zip_code=ZIP,
            property_type="Single Family",
            zoning_status="Pending",
        )
    )
    db.add(
        Property(
            id="stable",
            user_id=HOST_A,
            address=SHORT,
            city=CITY,
            state=STATE,
            zip_code=ZIP,
            property_type="Single Family",
            zoning_status="Pending",
        )
    )
    db.commit()
    result = cleanup_host_duplicates(db, HOST_A)
    db.commit()
    ids = {p.id for p in db.query(Property).filter(Property.user_id == HOST_A).all()}
    assert ids == {"oak", "stable"}
    assert result.groups_merged == 0
    db.close()


def test_cross_host_intact():
    _seed_property(HOST_A, SHORT)
    _seed_property(HOST_B, FULL)
    db = TestingSessionLocal()
    cleanup_host_duplicates(db, HOST_A)
    cleanup_host_duplicates(db, HOST_B)
    db.commit()
    assert db.query(Property).filter(Property.user_id == HOST_A).count() == 1
    assert db.query(Property).filter(Property.user_id == HOST_B).count() == 1
    # Other host still not a duplicate for HOST_A prevent
    hit = find_host_duplicate_property(db, HOST_A, FULL, "", "", "")
    assert hit is not None and hit.user_id == HOST_A
    miss = find_host_duplicate_property(db, HOST_A, OTHER_STREET, CITY, STATE, ZIP)
    assert miss is None
    db.close()


def test_inventory_mentions_us018c():
    assert INVENTORY.is_file()
    text = INVENTORY.read_text()
    if CHANGELOG.is_file():
        text += CHANGELOG.read_text()
    assert "US-018c" in text or "TE-011" in text or "normalize" in text.lower()
