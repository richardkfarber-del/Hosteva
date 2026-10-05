"""Seed reruns must not recreate the municipal_codes stubs deleted 2026-09-28.

- Legacy "City of Miami Beach" + dead zoning URL must not be inserted.
- State of Florida keep row is FL-STATE-LICENSE (or name + State type), not a
  blank DBPR-VR-LICENSE duplicate.
"""
import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_seed_compliance_no_stubs.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_seed_compliance_no_stubs.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-seed-compliance-no-stubs")

from app.database import Base
from app.db_models import Ordinance
from app.models.compliance import MunicipalCode
from scripts import seed_compliance_rules as seed_mod
from scripts.seed_compliance_rules import (
    FL_KEEP_SOURCE_URL,
    FL_MUNICIPALITY_NAME,
    FL_STATE_ORDINANCE,
    MB_CURATED_SOURCE_URL,
    MB_DEAD_ZONING_SOURCE_URL,
    MB_MUNICIPALITY_NAME,
)

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)

FL_KEEP_SOURCE = FL_KEEP_SOURCE_URL


def _run_seed(db, monkeypatch):
    monkeypatch.setattr(seed_mod, "SessionLocal", lambda: db)
    original_close = db.close
    db.close = lambda: None
    try:
        seed_mod.seed_data()
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


def _names(db, name):
    return db.query(MunicipalCode).filter(MunicipalCode.municipality_name == name).all()


def test_rerun_finds_keep_rows_and_does_not_recreate_stubs(db, monkeypatch):
    """Prod-shaped keep rows: Miami Beach curated URL, Florida FL-STATE-LICENSE."""
    mb_id = uuid.uuid4()
    fl_id = uuid.uuid4()
    db.add(MunicipalCode(
        id=mb_id,
        municipality_name=MB_MUNICIPALITY_NAME,
        ordinance_number="MB-CURATED-KEEP",
        jurisdiction_type="City",
        state="FL",
        source_url=MB_CURATED_SOURCE_URL,
        requires_permit=True,
        permit_name="Miami Beach STR Certificate",
        is_allowed=False,
        str_prohibited=True,
        is_expert_verified=True,
    ))
    db.add(MunicipalCode(
        id=fl_id,
        municipality_name=FL_MUNICIPALITY_NAME,
        ordinance_number=FL_STATE_ORDINANCE,
        jurisdiction_type="State",
        state="FL",
        source_url=FL_KEEP_SOURCE,
        requires_permit=True,
        is_allowed=True,
        str_prohibited=False,
        is_expert_verified=False,
    ))
    db.commit()

    _run_seed(db, monkeypatch)
    _run_seed(db, monkeypatch)

    city_of = _names(db, "City of Miami Beach")
    assert city_of == []
    assert db.query(MunicipalCode).filter(
        MunicipalCode.ordinance_number == "DBPR-VR-LICENSE"
    ).count() == 0

    mb_rows = _names(db, MB_MUNICIPALITY_NAME)
    assert len(mb_rows) == 1
    assert mb_rows[0].id == mb_id
    assert mb_rows[0].source_url == MB_CURATED_SOURCE_URL
    assert MB_DEAD_ZONING_SOURCE_URL not in (mb_rows[0].source_url or "")
    assert mb_rows[0].ordinance_number == "MB-CURATED-KEEP"
    assert mb_rows[0].is_expert_verified is True
    assert mb_rows[0].jurisdiction_type == "City"
    assert mb_rows[0].state == "FL"

    fl_rows = _names(db, FL_MUNICIPALITY_NAME)
    assert len(fl_rows) == 1
    assert fl_rows[0].id == fl_id
    assert fl_rows[0].ordinance_number == FL_STATE_ORDINANCE
    assert fl_rows[0].source_url == FL_KEEP_SOURCE
    assert fl_rows[0].is_expert_verified is False
    assert fl_rows[0].requires_permit is True

    md = db.query(MunicipalCode).filter_by(
        municipality_name="Miami-Dade County",
        ordinance_number="MDC-BTR-CU",
    ).all()
    assert len(md) == 1

    assert db.query(Ordinance).filter_by(jurisdiction="City of Miami Beach").count() == 1
    assert db.query(Ordinance).filter_by(jurisdiction="Florida").count() == 1


def test_florida_state_type_match_survives_ordinance_rename(db, monkeypatch):
    fl_id = uuid.uuid4()
    db.add(MunicipalCode(
        id=fl_id,
        municipality_name=FL_MUNICIPALITY_NAME,
        ordinance_number="RENAMED-KEEP",
        jurisdiction_type="State",
        state="FL",
        source_url=FL_KEEP_SOURCE,
        requires_permit=True,
        is_expert_verified=False,
    ))
    db.commit()

    _run_seed(db, monkeypatch)

    fl_rows = _names(db, FL_MUNICIPALITY_NAME)
    assert len(fl_rows) == 1
    assert fl_rows[0].id == fl_id
    assert fl_rows[0].ordinance_number == "RENAMED-KEEP"
    assert fl_rows[0].source_url == FL_KEEP_SOURCE
    assert fl_rows[0].is_expert_verified is False
    assert db.query(MunicipalCode).filter(
        MunicipalCode.ordinance_number == "DBPR-VR-LICENSE"
    ).count() == 0


def test_missing_rows_use_keep_pattern_not_legacy_stubs(db, monkeypatch):
    _run_seed(db, monkeypatch)

    assert _names(db, "City of Miami Beach") == []
    mb_rows = _names(db, MB_MUNICIPALITY_NAME)
    assert len(mb_rows) == 1
    assert mb_rows[0].jurisdiction_type == "City"
    assert mb_rows[0].state == "FL"
    assert mb_rows[0].source_url == MB_CURATED_SOURCE_URL
    assert mb_rows[0].source_url != MB_DEAD_ZONING_SOURCE_URL

    fl_rows = _names(db, FL_MUNICIPALITY_NAME)
    assert len(fl_rows) == 1
    assert fl_rows[0].ordinance_number == FL_STATE_ORDINANCE
    assert fl_rows[0].jurisdiction_type == "State"
    assert fl_rows[0].source_url == FL_KEEP_SOURCE_URL
    assert fl_rows[0].requires_permit is True
    # Create-if-missing does not mark the state row expert-verified.
    assert fl_rows[0].is_expert_verified is False

    assert db.query(MunicipalCode).filter(
        MunicipalCode.ordinance_number == "DBPR-VR-LICENSE"
    ).count() == 0


def test_dead_zoning_url_on_miami_beach_row_is_replaced(db, monkeypatch):
    mb_id = uuid.uuid4()
    db.add(MunicipalCode(
        id=mb_id,
        municipality_name=MB_MUNICIPALITY_NAME,
        ordinance_number="MB-STR-PROHIBITION",
        jurisdiction_type="City",
        state="FL",
        source_url=MB_DEAD_ZONING_SOURCE_URL,
        requires_permit=True,
        permit_name="Miami Beach STR Certificate / Zoning Review",
        is_expert_verified=True,
    ))
    db.commit()

    _run_seed(db, monkeypatch)

    mb_rows = _names(db, MB_MUNICIPALITY_NAME)
    assert len(mb_rows) == 1
    assert mb_rows[0].id == mb_id
    assert mb_rows[0].source_url == MB_CURATED_SOURCE_URL
    assert _names(db, "City of Miami Beach") == []
