"""EPIC-RULES: Complete seed (all states), FL Covered gate, research queue, honest copy."""
import os
import uuid
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite:///./test_epic_rules_coverage.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_epic_rules_coverage.db"
os.environ["ENVIRONMENT"] = "test"
os.environ["BILLING_ENABLED"] = "false"
os.environ["JWT_SECRET_KEY"] = "test-epic-rules"
os.environ["RESEARCH_ADMIN_KEY"] = "test-admin-key"

from app.main import app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode, HOARule
from app.models.research_request import ResearchRequest
from scripts.seed_rules import seed_rules, complete_xlsx_present

REPO_ROOT = Path(__file__).resolve().parents[1]

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
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


def test_complete_xlsx_present_in_repo():
    assert complete_xlsx_present(str(REPO_ROOT)) is True


def test_seed_imports_all_states_fl_verified_non_fl_thin(db, tmp_path):
    """SP-010: import ALL Complete states; FL expert_verified; non-FL Thin/research."""
    phase3 = tmp_path / "Hosteva Phase III"
    phase3.mkdir()
    df = pd.DataFrame({
        "Jurisdiction Name": ["Kissimmee", "Austin", "Miami Beach", "Bay County"],
        "Jurisdiction Type": ["City", "City", "City", "County"],
        "State": ["FL", "TX", "FL", "FL"],
        "STR Permitted?": ["Restricted by Zoning", "Yes", "Banned", "Yes"],
        "Permit/License Required?": ["Yes", "Yes", "Yes", "Yes"],
        "Minimum Stay Requirement": ["None", "None", "None", "None"],
        "Occupancy Limits": ["max 10", "max 8", "NaN", "max 12"],
        "One-Time Registration Fee": [100, 50, 0, 0],
        "Annual Renewal Fee": [50, 25, 0, 0],
        "Transient Occupancy Tax Rate": [0.06, 0.09, 0, 0.05],
        "Source URL": [
            "https://example.gov/kissimmee",
            "https://example.gov/austin",
            "https://example.gov/mb",
            "https://www.baycountyfl.gov/",
        ],
        "Last Verified Date": ["2026-06-05"] * 4,
    })
    df.to_excel(phase3 / "Hosteva Jurisdictional Rules DB (Complete).xlsx", index=False)

    # Also write HOA v5
    hoa = pd.DataFrame({
        "HOA Name": ["Solara Resort", "Desert Oasis"],
        "Location (City/County)": ["Osceola County", "Maricopa County, AZ"],
        "STR Permitted?": ["Yes", "Restricted"],
        "Minimum Lease/Stay": ["Nightly", "30 days"],
        "Rules Available Y/N": ["Yes", "Yes"],
        "Official Website": ["http://solara", "http://desert"],
        "Last Confirmed Date": ["2026-06-07", "2026-06-07"],
        "Key Rules & STR Restrictions (Notes)": ["FL notes", "AZ notes"],
    })
    hoa.to_excel(tmp_path / "Hosteva HOA STR Rules Database (Complete v5).xlsx", index=False)

    stats = seed_rules(db, str(tmp_path))
    assert stats["is_complete"] is True
    assert stats["municipal_fl"] == 3
    assert stats["municipal_non_fl"] == 1
    assert db.query(MunicipalCode).count() == 4

    fl = db.query(MunicipalCode).filter(MunicipalCode.state == "FL").all()
    assert all(r.is_expert_verified for r in fl)
    tx = db.query(MunicipalCode).filter(MunicipalCode.state == "TX").one()
    assert tx.is_expert_verified is False
    assert tx.is_ai_scraped is False
    assert getattr(tx, "source_kind", None) in ("excel_seed", None) or tx.source_kind == "excel_seed"

    assert db.query(HOARule).count() == 2
    assert "Complete v5" in (stats["hoa_source"] or "")


def test_seed_upsert_complete_wins(db, tmp_path):
    """Denser Complete upsert updates existing Phase-1-style row."""
    # Phase 1 style first
    df1 = pd.DataFrame({
        "Jurisdiction Name": ["Kissimmee"],
        "Jurisdiction Type": ["City"],
        "STR Permitted?": ["Yes"],
        "Permit/License Required?": ["No"],
        "Minimum Stay Requirement": ["None"],
        "Occupancy Limits": ["max 4"],
        "Tax Rate / Registration Fee": ["5% Tax"],
        "Source URL": ["http://old"],
        "Last Verified Date": ["2026-01-01"],
    })
    df1.to_excel(tmp_path / "Hosteva Jurisdictional Rules DB - Florida Counties (Phase 1).xlsx", index=False)
    seed_rules(db, str(tmp_path))
    row = db.query(MunicipalCode).filter_by(municipality_name="Kissimmee").one()
    assert row.source_url == "http://old"
    assert row.requires_permit is False

    # Now Complete present — denser wins
    phase3 = tmp_path / "Hosteva Phase III"
    phase3.mkdir()
    df2 = pd.DataFrame({
        "Jurisdiction Name": ["Kissimmee"],
        "Jurisdiction Type": ["City"],
        "State": ["FL"],
        "STR Permitted?": ["Restricted by Zoning"],
        "Permit/License Required?": ["Yes"],
        "Minimum Stay Requirement": ["None"],
        "Occupancy Limits": ["max 10"],
        "One-Time Registration Fee": [100],
        "Annual Renewal Fee": [50],
        "Transient Occupancy Tax Rate": [0.06],
        "Source URL": ["http://complete"],
        "Last Verified Date": ["2026-06-05"],
    })
    df2.to_excel(phase3 / "Hosteva Jurisdictional Rules DB (Complete).xlsx", index=False)
    seed_rules(db, str(tmp_path))
    row = db.query(MunicipalCode).filter_by(municipality_name="Kissimmee", state="FL").one()
    assert row.source_url == "http://complete"
    assert row.requires_permit is True
    assert db.query(MunicipalCode).count() == 1


@patch("app.api.v1.compliance.geocode_address")
def test_non_fl_research_seed_still_under_review(mock_geocode, client, db):
    """Non-FL MunicipalCode seed must not become Covered."""
    db.add(MunicipalCode(
        id=uuid.uuid4(),
        municipality_name="Austin",
        ordinance_number="TX-AUS",
        jurisdiction_type="City",
        state="TX",
        is_allowed=True,
        str_prohibited=False,
        requires_permit=True,
        is_expert_verified=False,
        source_kind="excel_seed",
    ))
    db.commit()
    mock_geocode.return_value = {"city": "Austin", "county": "Travis County", "state": "TX", "address_components": []}
    res = client.get("/api/v1/compliance", params={"address": "1 Congress Ave, Austin, TX"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_under_review"] is True
    assert data["status"] == "UNDER_REVIEW"
    assert data["is_compliant"] is False
    assert data.get("status_reason") == "OUT_OF_PACK_GEOGRAPHY"
    # Queue enqueued
    assert db.query(ResearchRequest).count() >= 1


@patch("app.api.v1.compliance.geocode_address")
def test_fl_miss_under_review_enqueues_research(mock_geocode, client, db):
    mock_geocode.return_value = {
        "city": "Unknownville",
        "county": "Nowhere County",
        "state": "FL",
        "address_components": [],
    }
    res = client.get("/api/v1/compliance", params={"address": "1 Nowhere Ln, FL"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "UNDER_REVIEW"
    assert data["is_compliant"] is False
    rows = db.query(ResearchRequest).all()
    assert len(rows) == 1
    assert rows[0].status == "queued"
    # Second miss bumps hit_count
    res2 = client.get("/api/v1/compliance", params={"address": "2 Nowhere Ln, FL"})
    assert res2.status_code == 200
    db.expire_all()
    rows = db.query(ResearchRequest).all()
    assert len(rows) == 1
    assert rows[0].hit_count >= 2


@patch("app.api.v1.compliance.geocode_address")
def test_draft_ready_still_under_review(mock_geocode, client, db):
    db.add(ResearchRequest(
        id=uuid.uuid4(),
        jurisdiction_key="fl|unknownville|city",
        state="FL",
        municipality_name="Unknownville",
        jurisdiction_type="city",
        status="draft_ready",
        trigger_reason="MISSING_MUNICIPAL_CODE",
        priority=100,
        hit_count=1,
        draft_payload='{"source_kind":"ai_draft","confidence":"low"}',
    ))
    db.commit()
    mock_geocode.return_value = {
        "city": "Unknownville",
        "county": "Nowhere County",
        "state": "FL",
        "address_components": [],
    }
    res = client.get("/api/v1/compliance", params={"address": "1 Nowhere Ln, FL"})
    assert res.json()["status"] == "UNDER_REVIEW"
    assert res.json()["is_compliant"] is False


def test_admin_research_list_requires_key(client, db):
    r = client.get("/api/v1/admin/research-requests")
    assert r.status_code in (401, 503)
    r2 = client.get(
        "/api/v1/admin/research-requests",
        headers={"X-Admin-Key": "test-admin-key"},
    )
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)


def test_coverage_copy_surfaces(client):
    """SP-012: FL framing; no CA/TX/NY Covered laundry list."""
    for path in ("/", "/features", "/pricing"):
        body = client.get(path).text
        assert "Florida" in body
        assert "Under Review" in body
        # Hard bans from COVERAGE_COPY
        assert "10 states" not in body.lower()
        assert "spanning 10" not in body.lower()
        # Must not sell CA/TX/NY as Covered geography (honest "not multi-state" OK)
        for banned in ("Covered in California", "Covered in Texas", "Covered in New York"):
            assert banned not in body
        assert "we cover california" not in body.lower()
    features = client.get("/features").text
    assert "Where" in features and "Covered" in features


def test_eligibility_non_fl_under_review(client, db, monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "fake")

    class FakeResp:
        def json(self):
            return {
                "status": "OK",
                "results": [{
                    "formatted_address": "1 Main St, Springfield, IL",
                    "address_components": [
                        {"long_name": "Springfield", "short_name": "Springfield", "types": ["locality"]},
                        {"long_name": "Illinois", "short_name": "IL", "types": ["administrative_area_level_1"]},
                        {"long_name": "US", "short_name": "US", "types": ["country"]},
                    ],
                }],
            }

    with patch("app.routers.eligibility.requests.get", return_value=FakeResp()):
        r = client.post("/api/eligibility/check", json={"address": "1 Main St, Springfield, IL"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "UNDER_REVIEW"
    assert data.get("status_reason") == "OUT_OF_PACK_GEOGRAPHY"
