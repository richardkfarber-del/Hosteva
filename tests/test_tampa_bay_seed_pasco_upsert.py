"""Regression: Tampa Bay pack upsert vs existing Pasco JURISDICTION-RULES.

Prod every-deploy seed hit UniqueViolation on uq_municipal_codes_name_type
when Pasco already existed as ordinance_number=JURISDICTION-RULES (tax-only:
requires_permit=false, tax_rate=5.0). The pack used to INSERT PASCO-PERMIT-REQ
(CUP / permit=true / tax_rate=4.0) and roll back the whole transaction, so
PL-13 tax_registration_url never landed.

Guards:
- Existing JURISDICTION-RULES row is updated, not duplicated
- tax_registration_url + municipal source_url land
- CUP / permit=true / tax_rate=4.0 is not forced onto a tax-only live row
- UniqueViolation on insert is recovered; other pack rows still seed
"""
import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_tampa_bay_seed_pasco_upsert.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_tampa_bay_seed_pasco_upsert.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-tampa-bay-pasco-upsert")

from app.database import Base
from app.models.compliance import MunicipalCode
from scripts import seed_tampa_bay_rules as tampa_mod
from scripts.seed_tampa_bay_rules import (
    PASCO_MUNICIPAL_SOURCE_URL,
    PASCO_TAX_REGISTRATION_URL,
    apply_pack_update,
    find_existing_municipal_code,
)

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)


def _add_pasco_jurisdiction_rules(db, *, state="FL"):
    db.add(MunicipalCode(
        id=uuid.uuid4(),
        municipality_name="Pasco County",
        ordinance_number="JURISDICTION-RULES",
        jurisdiction_type="County",
        state=state,
        is_allowed=True,
        str_prohibited=False,
        requires_permit=False,
        permit_name=None,
        tax_rate=5.0,
        source_url="https://floridarevenue.com/Forms_library/current/dr15tdt.pdf",
        tax_registration_url=None,
        is_expert_verified=True,
        is_ai_scraped=False,
        source_kind="excel_seed",
    ))
    db.commit()


def _run_seed(db, monkeypatch):
    monkeypatch.setattr(tampa_mod, "SessionLocal", lambda: db)
    original_close = db.close
    db.close = lambda: None
    try:
        tampa_mod.seed_tampa_bay_rules()
    finally:
        db.close = original_close


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_find_matches_pasco_jurisdiction_rules_by_name(db):
    _add_pasco_jurisdiction_rules(db)
    rule = {
        "municipality_name": "Pasco County",
        "ordinance_number": "PASCO-PERMIT-REQ",
        "jurisdiction_type": "County",
        "state": "FL",
    }
    found = find_existing_municipal_code(db, rule)
    assert found is not None
    assert found.ordinance_number == "JURISDICTION-RULES"


def test_seed_updates_pasco_tax_url_without_unique_violation_or_cup(db, monkeypatch):
    """Prod-shaped row: JURISDICTION-RULES / permit=false / tax_rate=5.0."""
    _add_pasco_jurisdiction_rules(db)

    _run_seed(db, monkeypatch)

    rows = db.query(MunicipalCode).filter(
        MunicipalCode.municipality_name == "Pasco County"
    ).all()
    assert len(rows) == 1
    pasco = rows[0]
    assert pasco.ordinance_number == "JURISDICTION-RULES"
    assert pasco.tax_registration_url == PASCO_TAX_REGISTRATION_URL
    assert pasco.source_url == PASCO_MUNICIPAL_SOURCE_URL
    assert pasco.requires_permit is False
    assert pasco.tax_rate == 5.0
    assert pasco.permit_name not in ("Conditional Use Permit (CUP)", "Conditional Use Permit")
    assert "CUP" not in (pasco.permit_name or "")

    pcb = db.query(MunicipalCode).filter(
        MunicipalCode.municipality_name == "Panama City Beach"
    ).first()
    assert pcb is not None
    assert pcb.is_expert_verified is True


def test_seed_matches_pasco_when_state_is_null(db, monkeypatch):
    """Lookup by name+type+state=FL misses; must not INSERT a second Pasco row."""
    _add_pasco_jurisdiction_rules(db, state=None)

    _run_seed(db, monkeypatch)

    rows = db.query(MunicipalCode).filter(
        MunicipalCode.municipality_name == "Pasco County"
    ).all()
    assert len(rows) == 1
    pasco = rows[0]
    assert pasco.ordinance_number == "JURISDICTION-RULES"
    assert pasco.tax_registration_url == PASCO_TAX_REGISTRATION_URL
    assert pasco.requires_permit is False
    assert pasco.tax_rate == 5.0
    assert "CUP" not in (pasco.permit_name or "")


def test_seed_recovers_from_unique_violation_insert_path(db, monkeypatch):
    """If name+type lookup is skipped, INSERT hits unique and must update in place."""
    _add_pasco_jurisdiction_rules(db)
    monkeypatch.setattr(tampa_mod, "find_existing_municipal_code", lambda *_a, **_k: None)

    _run_seed(db, monkeypatch)

    rows = db.query(MunicipalCode).filter(
        MunicipalCode.municipality_name == "Pasco County"
    ).all()
    assert len(rows) == 1
    pasco = rows[0]
    assert pasco.tax_registration_url == PASCO_TAX_REGISTRATION_URL
    assert pasco.requires_permit is False
    assert "CUP" not in (pasco.permit_name or "")


def test_soft_update_does_not_force_cup_onto_tax_only_pasco(db):
    """Even a CUP-shaped pack must only write URL fields onto a tax-only live row."""
    _add_pasco_jurisdiction_rules(db)
    existing = db.query(MunicipalCode).filter(
        MunicipalCode.municipality_name == "Pasco County"
    ).one()
    cup_pack = {
        "municipality_name": "Pasco County",
        "ordinance_number": "PASCO-PERMIT-REQ",
        "str_prohibited": False,
        "requires_permit": True,
        "permit_name": "Conditional Use Permit (CUP)",
        "tax_rate": 4.0,
        "source_url": PASCO_MUNICIPAL_SOURCE_URL,
        "tax_registration_url": PASCO_TAX_REGISTRATION_URL,
        "stay_restriction_days": None,
        "max_rentals_per_year": None,
        "jurisdiction_type": "County",
        "state": "FL",
        "is_expert_verified": True,
        "source_kind": "manual_pack",
    }

    mode = apply_pack_update(existing, cup_pack)
    db.commit()

    assert mode == "soft"
    assert existing.requires_permit is False
    assert existing.tax_rate == 5.0
    assert existing.permit_name is None
    assert existing.ordinance_number == "JURISDICTION-RULES"
    assert existing.tax_registration_url == PASCO_TAX_REGISTRATION_URL
    assert existing.source_url == PASCO_MUNICIPAL_SOURCE_URL
