"""PL-13 / US-020 + US-021 + TE-013 — checklist CTA + tax URL split.

Guards:
- No UI string "Open free checklist" (wizard + dashboard); guests keep Sign Up
- Logged-in Covered CTA has no free-checklist button
- municipal_code.tax_registration_url is distinct from source_url
- Oak Drive / Pasco Tax Registration → Tourist Express, not DR-15 PDF
- Checklist builder does not copy municipal source_url onto tax items
- Out of scope: Curated allowlist and Under Review gate unchanged
"""
import os
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pl13_checklist_cta_tax.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_pl13_checklist_cta_tax.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-pl13-cta-tax")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode
from app.api.v1.compliance import municipal_vs_tax_source_url
from scripts.seed_tampa_bay_rules import (
    DR15_TDT_PDF_URL,
    PASCO_MUNICIPAL_SOURCE_URL,
    PASCO_TAX_INFO_URL,
    PASCO_TAX_REGISTRATION_URL,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
WIZARD = (REPO_ROOT / "app" / "templates" / "wizard.html").read_text()
DASHBOARD = (REPO_ROOT / "app" / "templates" / "dashboard.html").read_text()
BYL_PAGE = (REPO_ROOT / "app" / "templates" / "before_you_list.html").read_text()
SEED = (REPO_ROOT / "scripts" / "seed_tampa_bay_rules.py").read_text()
HUDSON = "10703 Oak Drive, Hudson, FL 34667"

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _seed_pasco(db):
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
        tax_rate=4.0,
        source_url=PASCO_MUNICIPAL_SOURCE_URL,
        tax_registration_url=PASCO_TAX_REGISTRATION_URL,
        is_expert_verified=True,
        is_ai_scraped=False,
    ))
    db.commit()


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        _seed_pasco(session)
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


def test_us020_no_open_free_checklist_in_templates():
    for name, html in (("wizard", WIZARD), ("dashboard", DASHBOARD), ("before_you_list", BYL_PAGE)):
        assert "Open free checklist" not in html, name
    assert "openFreeChecklistBtn" not in WIZARD
    assert "Create a free account to see your checklist" in WIZARD
    assert "Eligibility Audit" in WIZARD
    assert "Before you list" in DASHBOARD
    assert "data-cta-state=\"logged-in-covered\"" in WIZARD
    logged_in = WIZARD.split("if (isLoggedIn)")[1].split("const registerUrl")[0]
    assert "Create a free account to see your checklist" not in logged_in
    assert "openFreeChecklistBtn" not in logged_in


def test_us020_wizard_guest_signup_still_present():
    res = TestClient(app).get("/wizard")
    assert res.status_code == 200
    assert "Create a free account to see your checklist" in res.text
    assert "Open free checklist" not in res.text
    assert "tax_registration_url" in res.text
    assert 'data-link-role="tax-registration"' in res.text


def test_te013_helper_does_not_copy_municipal_onto_tax():
    mc = SimpleNamespace(
        source_url="https://www.pascocountyfl.gov/",
        tax_registration_url=PASCO_TAX_REGISTRATION_URL,
    )
    assert municipal_vs_tax_source_url(mc, "Pasco Conditional Use Permit", kind="permit") == mc.source_url
    assert municipal_vs_tax_source_url(mc, "Tax Registration (4% TDT)", kind="tax") == PASCO_TAX_REGISTRATION_URL
    missing_tax = SimpleNamespace(source_url=mc.source_url, tax_registration_url=None)
    assert municipal_vs_tax_source_url(missing_tax, "Tax Registration (4% TDT)") is None
    assert municipal_vs_tax_source_url(None, "Tax Registration (4% TDT)") is None


@patch("app.api.v1.compliance.geocode_address")
def test_us021_oak_drive_tax_uses_tourist_express(mock_geocode, client):
    mock_geocode.return_value = {
        "city": "Hudson",
        "county": "Pasco County",
        "state": "FL",
        "postal_code": "34667",
        "address_components": [],
    }
    data = client.get("/api/v1/compliance", params={"address": HUDSON}).json()
    assert data["is_under_review"] is False
    mc = data["municipal_code"]
    assert mc["municipality_name"] == "Pasco County"
    assert mc["source_url"] == PASCO_MUNICIPAL_SOURCE_URL
    assert mc["tax_registration_url"] == PASCO_TAX_REGISTRATION_URL
    assert mc["source_url"] != mc["tax_registration_url"]
    assert DR15_TDT_PDF_URL not in (mc["source_url"] or "")
    assert DR15_TDT_PDF_URL not in (mc["tax_registration_url"] or "")

    tax_items = [i for i in data["checklist"] if "Tax Registration" in (i.get("task_name") or "")]
    permit_items = [i for i in data["checklist"] if "Permit" in (i.get("task_name") or "")]
    assert tax_items
    assert permit_items
    assert tax_items[0]["source_url"] == PASCO_TAX_REGISTRATION_URL
    assert tax_items[0]["source_url"] != PASCO_TAX_INFO_URL
    assert permit_items[0]["source_url"] == PASCO_MUNICIPAL_SOURCE_URL
    assert tax_items[0]["source_url"] != permit_items[0]["source_url"]
    assert DR15_TDT_PDF_URL not in (tax_items[0]["source_url"] or "")


def test_te013_pasco_seed_splits_municipal_and_tax():
    assert PASCO_TAX_REGISTRATION_URL in SEED
    assert "pasco.county-taxes.com/tourist" in SEED
    assert "tax_registration_url" in SEED
    # DR-15 may be named as the forbidden URL; must not be assigned as Pasco source or tax
    pasco_block = SEED.split('"municipality_name": "Pasco County"')[1].split('"municipality_name":')[0]
    assert "PASCO_TAX_REGISTRATION_URL" in pasco_block or PASCO_TAX_REGISTRATION_URL in pasco_block
    assert "PASCO_MUNICIPAL_SOURCE_URL" in pasco_block or PASCO_MUNICIPAL_SOURCE_URL in pasco_block
    assert f'"source_url": "{DR15_TDT_PDF_URL}"' not in pasco_block
    assert f'"tax_registration_url": "{DR15_TDT_PDF_URL}"' not in pasco_block


def test_pl13_does_not_expand_curated_allowlist():
    curated = (REPO_ROOT / "app" / "services" / "curated_coverage.py").read_text().lower()
    assert "hernando" not in curated
