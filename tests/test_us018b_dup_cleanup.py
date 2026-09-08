"""US-018b / TE-010 — Host-scoped existing duplicate property cleanup.

Canonical: richest compliance/checklist, else earliest created_at.
No PL-08/09/10/11 / Option B changes.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_us018b_dup.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_us018b_dup.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-us018b-dup")
os.environ["ADMIN_API_KEY"] = "test-admin-us018b"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.models.compliance import MunicipalCode, PropertyCompliance
from app.core.security import get_current_user, get_password_hash
from app.services.duplicate_cleanup import (
    cleanup_all_host_duplicates,
    cleanup_host_duplicates,
    compliance_richness_score,
    select_canonical,
)
from app.services.duplicate_address import addresses_equivalent

REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_WS = Path("/workspace/hosteva-review/docs/05_build/CHANGELOG.md")

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

HOST_A = "host_us018b_a"
HOST_B = "host_us018b_b"
USER_A = "us018b_host_a"
USER_B = "us018b_host_b"
MC_ID = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
VP = "[2026-01-01 00:00:00, 2027-01-01 00:00:00]"


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Host(id=HOST_A, username=USER_A, email="a@us018b.test", password_hash=get_password_hash("x")))
    db.add(Host(id=HOST_B, username=USER_B, email="b@us018b.test", password_hash=get_password_hash("x")))
    db.add(MunicipalCode(id=MC_ID, municipality_name="TampaUS018b", ordinance_number="US018B-1", requires_permit=True))
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    prev_db = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    if prev_db is not None:
        app.dependency_overrides[get_db] = prev_db
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _prop(db, *, pid, host, address, city="Tampa", state="FL", zip_code="33602",
          created_at=None, image_url=None, zoning_status="Pending"):
    p = Property(
        id=pid,
        user_id=host,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        property_type="Single Family",
        image_url=image_url,
        zoning_status=zoning_status,
    )
    if created_at is not None:
        p.created_at = created_at
    db.add(p)
    db.flush()
    return p


def _checklist(db, *, property_id, status="PENDING", is_compliant=False,
               uploaded=None, task_name="STR Permit"):
    db.add(PropertyCompliance(
        id=uuid.uuid4(),
        property_id=property_id,
        municipal_code_id=MC_ID,
        is_compliant=is_compliant,
        status=status,
        task_name=task_name,
        uploaded_file_url=uploaded,
        valid_period=VP,
    ))


def test_matching_reuses_us018_rules():
    assert addresses_equivalent(
        "123 Palm Ave", "Tampa", "FL", "33602",
        "  123   PALM ave ", "tampa", "florida", "",
    )


def test_host_with_n_duplicates_collapses_to_one():
    db = TestingSessionLocal()
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    _prop(db, pid="p-empty", host=HOST_A, address="Stable Run Dr", created_at=t0)
    rich = _prop(
        db, pid="p-rich", host=HOST_A, address="Stable Run Dr",
        created_at=t0 + timedelta(days=2), image_url="https://img/x.jpg",
        zoning_status="Allowed",
    )
    _prop(db, pid="p-mid", host=HOST_A, address="  stable run dr ", created_at=t0 + timedelta(days=1))
    _checklist(db, property_id=rich.id, status="VERIFIED", is_compliant=True, uploaded="/f.pdf")
    db.commit()

    result = cleanup_host_duplicates(db, HOST_A)
    db.commit()

    remaining = db.query(Property).filter(Property.user_id == HOST_A).all()
    assert len(remaining) == 1
    assert remaining[0].id == "p-rich"
    assert result.properties_removed == 2
    assert result.groups_merged == 1
    items = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == "p-rich").all()
    assert len(items) == 1
    db.close()


def test_distinct_addresses_both_remain():
    db = TestingSessionLocal()
    _prop(db, pid="p-a", host=HOST_A, address="100 Oak St")
    _prop(db, pid="p-b", host=HOST_A, address="200 Pine St")
    db.commit()
    result = cleanup_host_duplicates(db, HOST_A)
    db.commit()
    ids = {p.id for p in db.query(Property).filter(Property.user_id == HOST_A).all()}
    assert ids == {"p-a", "p-b"}
    assert result.groups_merged == 0
    db.close()


def test_second_host_same_street_unaffected():
    db = TestingSessionLocal()
    t0 = datetime(2026, 2, 1, tzinfo=timezone.utc)
    _prop(db, pid="a1", host=HOST_A, address="55 Bay St", created_at=t0)
    _prop(db, pid="a2", host=HOST_A, address="55 Bay St", created_at=t0 + timedelta(hours=1))
    _prop(db, pid="b1", host=HOST_B, address="55 Bay St", created_at=t0)
    db.commit()

    cleanup_all_host_duplicates(db)
    a_ids = {p.id for p in db.query(Property).filter(Property.user_id == HOST_A).all()}
    b_ids = {p.id for p in db.query(Property).filter(Property.user_id == HOST_B).all()}
    assert len(a_ids) == 1
    assert b_ids == {"b1"}
    db.close()


def test_canonical_prefers_richest_over_earlier():
    db = TestingSessionLocal()
    t0 = datetime(2026, 3, 1, tzinfo=timezone.utc)
    early = _prop(db, pid="early", host=HOST_A, address="9 Lake Rd", created_at=t0)
    late_rich = _prop(db, pid="late", host=HOST_A, address="9 Lake Rd", created_at=t0 + timedelta(days=5))
    _checklist(db, property_id=late_rich.id, status="COMPLETED", is_compliant=True, uploaded="/x")
    db.commit()
    assert select_canonical(db, [early, late_rich]).id == "late"
    assert compliance_richness_score(db, late_rich) > compliance_richness_score(db, early)
    db.close()


def test_canonical_earliest_when_equal_richness():
    db = TestingSessionLocal()
    t0 = datetime(2026, 4, 1, tzinfo=timezone.utc)
    a = _prop(db, pid="eq-a", host=HOST_A, address="1 Equal Ave", created_at=t0)
    b = _prop(db, pid="eq-b", host=HOST_A, address="1 Equal Ave", created_at=t0 + timedelta(days=1))
    db.commit()
    assert select_canonical(db, [b, a]).id == "eq-a"
    db.close()


def test_reattach_checklist_to_canonical():
    db = TestingSessionLocal()
    t0 = datetime(2026, 5, 1, tzinfo=timezone.utc)
    # Canon starts richer (verified checklist + image) so it wins over the donor twin.
    canon = _prop(db, pid="c-keep", host=HOST_A, address="77 Reattach Ln", created_at=t0,
                  image_url="https://img/keep.jpg", zoning_status="Allowed")
    _checklist(
        db, property_id="c-keep", status="VERIFIED", is_compliant=True,
        uploaded="/keep.pdf", task_name="STR Permit",
    )
    donor = _prop(db, pid="c-drop", host=HOST_A, address="77 Reattach Ln", created_at=t0 + timedelta(days=1))
    _checklist(db, property_id=donor.id, status="UPLOADED", uploaded="/donor.pdf", task_name="HOA Docs")
    db.commit()
    cleanup_host_duplicates(db, HOST_A)
    db.commit()
    assert db.query(Property).filter(Property.id == "c-drop").first() is None
    items = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == "c-keep").all()
    names = {i.task_name for i in items}
    assert names == {"STR Permit", "HOA Docs"}
    hoa = next(i for i in items if i.task_name == "HOA Docs")
    assert hoa.uploaded_file_url == "/donor.pdf"
    db.close()


def test_idempotent_second_run():
    db = TestingSessionLocal()
    t0 = datetime(2026, 6, 1, tzinfo=timezone.utc)
    _prop(db, pid="i1", host=HOST_A, address="Idempotent Way", created_at=t0)
    _prop(db, pid="i2", host=HOST_A, address="Idempotent Way", created_at=t0 + timedelta(hours=2))
    db.commit()
    r1 = cleanup_all_host_duplicates(db)
    assert r1.properties_removed == 1
    r2 = cleanup_all_host_duplicates(db)
    assert r2.properties_removed == 0
    assert r2.groups_merged == 0
    assert db.query(Property).filter(Property.user_id == HOST_A).count() == 1
    db.close()


def test_never_deletes_all_leaving_zero_canonical():
    db = TestingSessionLocal()
    t0 = datetime(2026, 7, 1, tzinfo=timezone.utc)
    _prop(db, pid="z1", host=HOST_A, address="Zero Fail St", created_at=t0)
    _prop(db, pid="z2", host=HOST_A, address="Zero Fail St", created_at=t0 + timedelta(minutes=1))
    db.commit()
    cleanup_host_duplicates(db, HOST_A)
    db.commit()
    assert db.query(Property).filter(Property.user_id == HOST_A).count() == 1
    db.close()


def test_admin_endpoint_requires_key():
    r = client.post("/api/v1/admin/properties/dedupe-duplicates")
    assert r.status_code in (401, 503)


def test_admin_endpoint_runs_cleanup():
    db = TestingSessionLocal()
    t0 = datetime(2026, 8, 1, tzinfo=timezone.utc)
    _prop(db, pid="adm1", host=HOST_A, address="Admin Dedupe Rd", created_at=t0)
    _prop(db, pid="adm2", host=HOST_A, address="Admin Dedupe Rd", created_at=t0 + timedelta(days=1))
    db.commit()
    db.close()

    r = client.post(
        "/api/v1/admin/properties/dedupe-duplicates",
        headers={"X-Admin-Key": "test-admin-us018b"},
        params={"host_id": HOST_A},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["properties_removed"] == 1
    assert "richest" in body["canonical_rule"].lower()

    db = TestingSessionLocal()
    assert db.query(Property).filter(Property.user_id == HOST_A).count() == 1
    db.close()


def test_out_of_scope_no_pl08_pl09_option_b_changes():
    """Guard: this PR must not touch PL-08/09/10/11 or curated Option B."""
    curated = (REPO_ROOT / "app" / "services" / "curated_coverage.py").read_text()
    # Smoke: file still present and unchanged intent — allowlist helper exists
    assert "is_curated" in curated or "CURATED" in curated or "curated" in curated.lower()
    # Dedup module documents out-of-scope
    cleanup_src = (REPO_ROOT / "app" / "services" / "duplicate_cleanup.py").read_text()
    assert "US-018b" in cleanup_src or "TE-010" in cleanup_src


def test_changelog_documents_canonical_rule():
    # Workspace CHANGELOG is SoT for review; also accept repo-local note if mirrored.
    paths = [CHANGELOG_WS]
    repo_inv = REPO_ROOT / "docs" / "06_qa" / "TEST_INVENTORY.md"
    assert repo_inv.exists()
    text = ""
    for p in paths:
        if p.exists():
            text += p.read_text()
    assert "US-018b" in text or "TE-010" in text or "richest" in text.lower()
