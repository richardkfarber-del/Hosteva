"""Cheap MB eligibility: City of Miami Beach seed must not stay UNDER_REVIEW."""
import os
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_elig_mb_city_of.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_elig_mb_city_of.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-elig-mb")

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode
from app.routers.eligibility import _lookup_municipal

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
    db.query(MunicipalCode).delete()
    db.add(MunicipalCode(
        id=uuid.uuid4(),
        municipality_name="City of Miami Beach",
        ordinance_number="MB-TEST-1",
        jurisdiction_type=None,
        state="FL",
        is_allowed=True,
        str_prohibited=False,
        requires_permit=True,
    ))
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    prev = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    yield
    if prev is not None:
        app.dependency_overrides[get_db] = prev
    else:
        app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_lookup_municipal_city_of_alias():
    db = TestingSessionLocal()
    try:
        row = _lookup_municipal(db, "Miami Beach", "Miami-Dade County", "FL")
        assert row is not None
        assert "Miami Beach" in row.municipality_name
    finally:
        db.close()


def test_eligibility_mb_convention_center_allowed_with_checklist(monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "fake-key")

    class FakeResp:
        def json(self):
            return {
                "status": "OK",
                "results": [{
                    "formatted_address": "1700 Convention Center Dr, Miami Beach, FL 33139, USA",
                    "address_components": [
                        {"long_name": "Miami Beach", "short_name": "Miami Beach", "types": ["locality"]},
                        {"long_name": "Miami-Dade County", "short_name": "Miami-Dade County", "types": ["administrative_area_level_2"]},
                        {"long_name": "Florida", "short_name": "FL", "types": ["administrative_area_level_1"]},
                        {"long_name": "US", "short_name": "US", "types": ["country"]},
                        {"long_name": "33139", "short_name": "33139", "types": ["postal_code"]},
                    ],
                }],
            }

    with patch("app.routers.eligibility.requests.get", return_value=FakeResp()):
        r = client.post(
            "/api/eligibility/check",
            json={"address": "1700 Convention Center Dr, Miami Beach, FL 33139"},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ALLOWED_WITH_CHECKLIST"
    assert data["status"] != "UNDER_REVIEW"
    assert "Miami Beach" in (data.get("municipality_name") or "")
