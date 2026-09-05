"""BUG-PL-07: POST /api/properties/ must not 500 when image/geocode/seed fail.

Widow: Kissimmee (301 E Dakin) + PCB (17001 Panama City Beach Pkwy) → 500/502
while Miami Beach Convention Center still 201. Existing corridor listings OK.
"""
import os
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_bug_pl07_create.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_bug_pl07_create.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-pl07-create")

import pytest
from unittest.mock import patch, MagicMock
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
from app.routers.properties import (
    FALLBACK_PROPERTY_IMAGE_URL,
    fetch_real_property_image,
    is_fallback_property_image,
    resolve_property_create_image,
)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

KISSIMMEE = {
    "address": "301 E Dakin Ave",
    "city": "Kissimmee",
    "state": "FL",
    "zip_code": "34741",
    "property_type": "Single Family",
}
PCB = {
    "address": "17001 Panama City Beach Pkwy",
    "city": "Panama City Beach",
    "state": "FL",
    "zip_code": "32413",
    "property_type": "Single Family",
}
MB = {
    "address": "1700 Convention Center Dr",
    "city": "Miami Beach",
    "state": "FL",
    "zip_code": "33139",
    "property_type": "Single Family",
}


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Host(
        id="host_pl07",
        username="pl07_host",
        email="pl07@host.test",
        password_hash=get_password_hash("x"),
    ))
    for name in ("Kissimmee", "Panama City Beach", "Miami Beach"):
        db.add(MunicipalCode(
            id=uuid.uuid4(),
            municipality_name=name,
            ordinance_number=f"PL07-{name.replace(' ', '-')[:12]}",
            jurisdiction_type="City",
            state="FL",
            is_allowed=True,
            str_prohibited=False,
            requires_permit=True,
            is_ai_scraped=False,
            is_expert_verified=True,
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
    app.dependency_overrides[get_current_user] = lambda: {"username": "pl07_host", "role": "host"}
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


def _audit_ok():
    return {
        "legal_subdivision_name": "Test",
        "hoa_detected": False,
        "hoa_rules_available": False,
        "eligibility_status": "Pending",
        "required_permits": ["Florida DBPR License task"],
        "local_restrictions": {},
    }


def test_fetch_image_never_raises_when_geocode_explodes():
    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}, clear=False):
        with patch("app.routers.properties._try_street_view_image", return_value=None):
            with patch("app.routers.properties._try_places_photo", return_value=None):
                with patch("app.routers.properties.geocode_address", side_effect=RuntimeError("geo down")):
                    url = fetch_real_property_image("301 E Dakin Ave, Kissimmee, FL 34741")
    assert url == FALLBACK_PROPERTY_IMAGE_URL
    assert is_fallback_property_image(url) is True


def test_fetch_image_never_raises_on_malformed_geocode_payload():
    """formatted_address as a list used to TypeError on .strip() (uncaught)."""
    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}, clear=False):
        with patch("app.routers.properties._try_street_view_image", return_value=None):
            with patch("app.routers.properties._try_places_photo", return_value=None):
                url = fetch_real_property_image(
                    "17001 Panama City Beach Pkwy, Panama City Beach, FL 32413",
                    geocoded={
                        "formatted_address": ["not", "a", "string"],
                        "lat": object(),
                        "lng": object(),
                    },
                )
    assert url == FALLBACK_PROPERTY_IMAGE_URL


def test_resolve_create_image_swallows_inner_raise():
    with patch(
        "app.routers.properties._fetch_real_property_image_inner",
        side_effect=RuntimeError("sv/places exploded"),
    ):
        url = resolve_property_create_image("301 E Dakin Ave, Kissimmee, FL 34741")
    assert url == FALLBACK_PROPERTY_IMAGE_URL


@pytest.mark.parametrize("payload", [KISSIMMEE, PCB], ids=["kissimmee", "pcb"])
def test_create_corridor_when_geocode_raises(payload):
    with patch("app.routers.properties.geocode_address", side_effect=RuntimeError("geocode 500")):
        with patch("app.services.compliance.run_gemini_audit", return_value=_audit_ok()):
            r = client.post("/api/properties/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["address"] == payload["address"]
    assert data["image_url"] == FALLBACK_PROPERTY_IMAGE_URL
    assert data["image_is_placeholder"] is True


@pytest.mark.parametrize("payload", [KISSIMMEE, PCB], ids=["kissimmee", "pcb"])
def test_create_corridor_when_image_fetch_raises(payload):
    geo = {
        "city": payload["city"],
        "county": "Test County",
        "state": "FL",
        "address_components": [],
        "formatted_address": f"{payload['address']}, {payload['city']}, FL",
        "lat": 28.0,
        "lng": -81.0,
    }
    with patch("app.routers.properties.geocode_address", return_value=geo):
        with patch(
            "app.routers.properties.fetch_real_property_image",
            side_effect=RuntimeError("street view blew up"),
        ):
            with patch("app.services.compliance.run_gemini_audit", return_value=_audit_ok()):
                r = client.post("/api/properties/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["image_is_placeholder"] is True
    assert data["image_url"] == FALLBACK_PROPERTY_IMAGE_URL


def test_create_kissimmee_real_sv_still_201():
    geo = {
        "city": "Kissimmee",
        "county": "Osceola County",
        "state": "FL",
        "address_components": [{"long_name": "Kissimmee", "types": ["locality"]}],
        "formatted_address": "301 E Dakin Ave, Kissimmee, FL 34741, USA",
        "lat": 28.292,
        "lng": -81.407,
    }
    with patch("app.routers.properties.geocode_address", return_value=geo):
        with patch(
            "app.routers.properties.fetch_real_property_image",
            return_value="/static/property_images/kissimmee-real.jpg",
        ):
            with patch("app.services.compliance.run_gemini_audit", return_value=_audit_ok()):
                r = client.post("/api/properties/", json=KISSIMMEE)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["image_url"] == "/static/property_images/kissimmee-real.jpg"
    assert data["image_is_placeholder"] is False
    assert data["location"] == "Kissimmee, FL"


def test_create_when_audit_raises_still_201():
    geo = {
        "city": "Panama City Beach",
        "county": "Bay County",
        "state": "FL",
        "address_components": [],
        "formatted_address": "17001 Panama City Beach Pkwy, Panama City Beach, FL 32413, USA",
        "lat": 30.2,
        "lng": -85.8,
    }
    with patch("app.routers.properties.geocode_address", return_value=geo):
        with patch(
            "app.routers.properties.fetch_real_property_image",
            return_value=FALLBACK_PROPERTY_IMAGE_URL,
        ):
            with patch(
                "app.services.compliance.run_gemini_audit",
                side_effect=RuntimeError("gemini timeout"),
            ):
                r = client.post("/api/properties/", json=PCB)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["image_is_placeholder"] is True
    assert isinstance(data.get("required_permits"), list)


def test_create_when_seed_raises_still_201():
    geo = {
        "city": "Kissimmee",
        "county": "Osceola County",
        "state": "FL",
        "address_components": [],
        "formatted_address": "301 E Dakin Ave, Kissimmee, FL 34741, USA",
        "lat": 28.29,
        "lng": -81.40,
    }
    with patch("app.routers.properties.geocode_address", return_value=geo):
        with patch(
            "app.routers.properties.fetch_real_property_image",
            return_value=FALLBACK_PROPERTY_IMAGE_URL,
        ):
            with patch("app.services.compliance.run_gemini_audit", return_value=_audit_ok()):
                with patch(
                    "app.routers.properties._seed_create_checklist",
                    side_effect=RuntimeError("unique municipal / celery"),
                ):
                    r = client.post("/api/properties/", json=KISSIMMEE)
    assert r.status_code == 201, r.text
    assert r.json()["address"] == "301 E Dakin Ave"


def test_create_mb_contrast_still_201():
    geo = {
        "city": "Miami Beach",
        "county": "Miami-Dade County",
        "state": "FL",
        "address_components": [],
        "formatted_address": "1700 Convention Center Dr, Miami Beach, FL 33139, USA",
        "lat": 25.795,
        "lng": -80.128,
    }
    with patch("app.routers.properties.geocode_address", return_value=geo):
        with patch(
            "app.routers.properties.fetch_real_property_image",
            return_value="/static/property_images/mb-real.jpg",
        ):
            with patch("app.services.compliance.run_gemini_audit", return_value=_audit_ok()):
                r = client.post("/api/properties/", json=MB)
    assert r.status_code == 201, r.text
    assert r.json()["image_is_placeholder"] is False


def test_v1_create_when_image_raises():
    payload = {
        "address": {
            "address": "301 E Dakin Ave",
            "city": "Kissimmee",
            "state": "FL",
            "zip_code": "34741",
        },
        "property_type": "Single Family",
        "compliance_data": {
            "zoning_status": "Pending",
            "hoa_status": False,
            "required_permits": ["Florida DBPR License task"],
            "local_restrictions": {},
        },
    }
    with patch("app.routers.properties.geocode_address", side_effect=RuntimeError("geo")):
        with patch(
            "app.routers.properties.fetch_real_property_image",
            side_effect=RuntimeError("sv"),
        ):
            r = client.post("/api/v1/properties/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["address"] == "301 E Dakin Ave"
    assert data["image_url"] == FALLBACK_PROPERTY_IMAGE_URL
    assert data["image_is_placeholder"] is True
