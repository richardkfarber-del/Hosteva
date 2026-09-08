"""BUG-012 — Stable Run Spring Hill must resolve Pasco Curated, not Hernando UR.

Guards:
- ZIP 34610 / Pasco county truth → Covered (Checklist Available class)
- True Hernando address stays Under Review (no Hernando allowlist expand)
- Hudson / Pasco control still Covered
- curated_coverage.py must not gain Hernando
"""
import os
import uuid
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_bug_012_stable_run_pasco.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_bug_012_stable_run_pasco.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-bug-012-stable-run")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode
from app.services.curated_coverage import (
    FL_CURATED_ALLOWLIST,
    is_name_on_curated_allowlist,
)
from app.services.jurisdiction_resolve import (
    FL_ZIP_COUNTY_OVERRIDES,
    correct_geocode_components,
    lookup_municipal_code,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
STABLE_RUN = "15758 Stable Run Drive, Spring Hill, FL 34610"
HUDSON = "10703 Oak Drive, Hudson, FL 34667"
HERNANDO_CONTROL = "100 Main St, Brooksville, FL 34601"

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _seed_pasco_and_neighbors(db):
    db.add(MunicipalCode(
        id=uuid.uuid4(),
        municipality_name="Pasco County",
        ordinance_number="PASCO-PERMIT-REQ",
        jurisdiction_type="County",
        state="FL",
        is_allowed=True,
        str_prohibited=False,
        requires_permit=True,
        permit_name="Pasco Conditional Use Permit",
        tax_rate=5.0,
        source_url="https://www.pascocountyfl.gov/",
        is_expert_verified=True,
        is_ai_scraped=False,
    ))
    # Non-curated CDP city row — must NOT win over Pasco when county/ZIP is Pasco
    db.add(MunicipalCode(
        id=uuid.uuid4(),
        municipality_name="Spring Hill",
        ordinance_number="SH-CDP-THIN",
        jurisdiction_type="City",
        state="FL",
        is_allowed=True,
        str_prohibited=False,
        requires_permit=True,
        permit_name="Spring Hill (non-curated)",
        is_expert_verified=True,
        is_ai_scraped=False,
    ))
    # Thin Hernando county seed — must stay Under Review (not on Option B allowlist)
    db.add(MunicipalCode(
        id=uuid.uuid4(),
        municipality_name="Hernando County",
        ordinance_number="HERN-TDT-STUB",
        jurisdiction_type="County",
        state="FL",
        is_allowed=True,
        str_prohibited=False,
        requires_permit=False,
        is_expert_verified=True,
        is_ai_scraped=False,
    ))
    db.commit()


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        _seed_pasco_and_neighbors(session)
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def override_get_db():
        s = TestingSessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


def test_curated_allowlist_has_pasco_not_hernando():
    assert is_name_on_curated_allowlist("Pasco") is True
    assert is_name_on_curated_allowlist("Pasco County") is True
    assert is_name_on_curated_allowlist("Hernando") is False
    assert is_name_on_curated_allowlist("Hernando County") is False
    assert is_name_on_curated_allowlist("Spring Hill") is False
    assert "hernando" not in FL_CURATED_ALLOWLIST
    assert "hernando county" not in FL_CURATED_ALLOWLIST
    curated_src = (REPO_ROOT / "app" / "services" / "curated_coverage.py").read_text().lower()
    assert "hernando" not in curated_src


def test_zip_34610_overrides_hernando_geocode_to_pasco():
    city, county, state, zip_c = correct_geocode_components(
        city="Spring Hill",
        county="Hernando County",
        state="FL",
        postal_code="34610",
        address=STABLE_RUN,
    )
    assert zip_c == "34610"
    assert county == "Pasco County"
    assert FL_ZIP_COUNTY_OVERRIDES["34610"] == "Pasco County"


def test_lookup_prefers_pasco_over_spring_hill_city(db):
    row, city, county, state, zip_c = lookup_municipal_code(
        db,
        city="Spring Hill",
        county="Hernando County",  # mis-route
        state="FL",
        address=STABLE_RUN,
    )
    assert zip_c == "34610"
    assert county == "Pasco County"
    assert row is not None
    assert row.municipality_name == "Pasco County"


@patch("app.api.v1.compliance.geocode_address")
def test_stable_run_compliance_pasco_curated(mock_geocode, client):
    """Google often returns Spring Hill + Hernando; ZIP 34610 must yield Pasco Covered."""
    mock_geocode.return_value = {
        "city": "Spring Hill",
        "county": "Hernando County",
        "state": "FL",
        "postal_code": "34610",
        "address_components": [],
    }
    data = client.get("/api/v1/compliance", params={"address": STABLE_RUN}).json()
    assert data["is_under_review"] is False
    assert data.get("coverage_tier") == "CURATED"
    assert data["status"] == "ALLOWED_WITH_CHECKLIST"
    assert data["municipal_code"] is not None
    assert data["municipal_code"]["municipality_name"] == "Pasco County"
    assert data["checklist"]


@patch("app.api.v1.compliance.geocode_address")
def test_stable_run_pasco_county_from_geocode_still_covered(mock_geocode, client):
    """When geocode already has Pasco, prefer county over non-curated Spring Hill city."""
    mock_geocode.return_value = {
        "city": "Spring Hill",
        "county": "Pasco County",
        "state": "FL",
        "postal_code": "34610",
        "address_components": [],
    }
    data = client.get("/api/v1/compliance", params={"address": STABLE_RUN}).json()
    assert data["is_under_review"] is False
    assert data.get("coverage_tier") == "CURATED"
    assert data["municipal_code"]["municipality_name"] == "Pasco County"


@patch("app.api.v1.compliance.geocode_address")
def test_hudson_pasco_still_covered(mock_geocode, client):
    mock_geocode.return_value = {
        "city": "Hudson",
        "county": "Pasco County",
        "state": "FL",
        "postal_code": "34667",
        "address_components": [],
    }
    data = client.get("/api/v1/compliance", params={"address": HUDSON}).json()
    assert data["is_under_review"] is False
    assert data.get("coverage_tier") == "CURATED"
    assert data["municipal_code"]["municipality_name"] == "Pasco County"


@patch("app.api.v1.compliance.geocode_address")
def test_true_hernando_stays_under_review(mock_geocode, client):
    mock_geocode.return_value = {
        "city": "Brooksville",
        "county": "Hernando County",
        "state": "FL",
        "postal_code": "34601",
        "address_components": [],
    }
    data = client.get("/api/v1/compliance", params={"address": HERNANDO_CONTROL}).json()
    assert data["is_under_review"] is True
    assert data["status"] == "UNDER_REVIEW"
    assert data["is_compliant"] is False
    assert data["municipal_code"] is None
    # Thin Hernando seed present but not Curated
    assert data.get("status_reason") in ("THIN_COVERAGE", "MISSING_MUNICIPAL_CODE")
