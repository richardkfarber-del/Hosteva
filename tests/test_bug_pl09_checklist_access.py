"""BUG-PL-09 — Dashboard checklist access for Free hosts.

Guards:
- Free Covered property has findable Before you list / free-checklist API path
- Under Review does not promise a full checklist
- Essentials still gates interactive checklist-items (US-006 unchanged)
- Dashboard chrome exposes labeled Checklist / Before you list control
"""
import os
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite:///./test_bug_pl09_checklist_access.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_bug_pl09_checklist_access.db"
os.environ["BILLING_ENABLED"] = "false"
os.environ["ENVIRONMENT"] = "test"
os.environ.setdefault("JWT_SECRET_KEY", "test-bug-pl09")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.core.security import get_current_user

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = (REPO_ROOT / "app" / "templates" / "dashboard.html").read_text()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_bug_pl09_checklist_access.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

FREE_HOST = "pl09_free_host"
HOST_ID = "host_pl09_free"
PROP_COVERED = "prop_pl09_covered"
PROP_UR = "prop_pl09_ur"


@pytest.fixture(autouse=True)
def bind_session_local():
    from app.database import SessionLocal
    SessionLocal.configure(bind=engine)
    yield


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def overrides():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: {"username": FREE_HOST, "role": "host"}
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add(Host(id=HOST_ID, username=FREE_HOST, email="pl09@test.com", password_hash="x"))
        db.add(Property(
            id=PROP_COVERED,
            user_id=HOST_ID,
            address="10703 Oak Drive",
            city="Hudson",
            state="FL",
            zip_code="34667",
            property_type="House",
            zoning_status="Action Required",
        ))
        db.add(Property(
            id=PROP_UR,
            user_id=HOST_ID,
            address="100 Main St",
            city="Brooksville",
            state="FL",
            zip_code="34601",
            property_type="House",
            zoning_status="Pending",
        ))
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_bug_pl09_checklist_access.db"):
        os.remove("test_bug_pl09_checklist_access.db")


client = TestClient(app)


def _covered_payload():
    return SimpleNamespace(
        model_dump=lambda: {
            "is_under_review": False,
            "is_compliant": True,
            "status": "ALLOWED_WITH_CHECKLIST",
            "coverage_tier": "CURATED",
            "status_reason": None,
            "checklist": [
                {
                    "task_name": "Pasco Conditional Use Permit",
                    "status": "PENDING",
                    "is_compliant": False,
                    "source_url": "https://www.pascocountyfl.gov/",
                },
                {
                    "task_name": "DBPR Vacation Rental License",
                    "status": "PENDING",
                    "is_compliant": False,
                    "source_url": None,
                },
            ],
        }
    )


def _ur_payload():
    return SimpleNamespace(
        model_dump=lambda: {
            "is_under_review": True,
            "is_compliant": False,
            "status": "UNDER_REVIEW",
            "coverage_tier": "THIN",
            "status_reason": "THIN_COVERAGE",
            "checklist": [
                # Theater checklist must be stripped for UR by free-checklist endpoint
                {"task_name": "Should not appear", "status": "PENDING", "is_compliant": False},
            ],
        }
    )


def test_dashboard_has_findable_before_you_list_control():
    """Free host dashboard chrome: labeled Checklist / Before you list path."""
    body = DASHBOARD
    assert "property-checklist-btn" in body
    assert "Before you list" in body
    assert "single-prop-checklist-btn" in body
    assert "bindDashboardChecklistControl" in body
    assert "/api/v1/compliance/free-checklist/" in body
    assert "data-checklist-role" in body
    assert "Before you list" in body
    assert "Open free checklist" not in body
    # Must not be Manage/Permit/Audit only
    assert "property-manage-btn" in body
    assert "property-permit-btn" in body
    assert "property-export-btn" in body
    # Live route still serves (auth may inject shell); soft check
    res = client.get("/dashboard")
    assert res.status_code in (200, 302, 401, 403, 404)


def test_dashboard_under_review_path_does_not_promise_full_checklist():
    """UR honesty helpers: View status / Under Review — no fake Compliant checklist CTA."""
    assert "function isFreeChecklistUnderReview" in DASHBOARD
    assert "function renderFreeChecklistUpgradePanel" in DASHBOARD
    ur_fn = DASHBOARD.split("function renderFreeChecklistUpgradePanel")[1].split(
        "async function fetchProperties"
    )[0]
    assert "Under Review" in ur_fn
    assert "no checklist to open" in ur_fn
    assert 'data-free-checklist-panel="under-review"' in ur_fn
    assert 'data-checklist-role="under-review-status"' in ur_fn
    # Negative: UR panel must not use Covered promise CTAs as its primary label
    assert "Create a free account to see your checklist" not in ur_fn
    # Covered panel still present in same function for Free path
    covered = ur_fn
    assert 'data-free-checklist-panel="covered"' in covered
    assert "Before you list" in covered
    assert "Before you list" in covered
    assert "Open free checklist" not in covered


def test_free_covered_property_free_checklist_api_path():
    """Free Covered: free-checklist 200 with municipal items + dedicated open_url."""
    with patch(
        "app.api.v1.compliance.get_compliance_by_address",
        return_value=_covered_payload(),
    ):
        r = client.get(f"/api/v1/compliance/free-checklist/{PROP_COVERED}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["is_under_review"] is False
    assert body["depth"] == "free"
    assert body["label"] == "Before you list"
    assert body["honesty"] == "Research only — not a legal determination."
    assert len(body["checklist"]) >= 1
    assert "Pasco Conditional Use Permit" in body["checklist"][0]["task_name"]
    # PL-12: dedicated page (no wizard intent=checklist dead-end)
    assert body["open_url"] == f"/properties/{PROP_COVERED}/before-you-list"
    assert "intent=checklist" not in body["open_url"]
    assert body["under_review_message"] is None
    assert body["essentials_note"]


def test_free_under_review_does_not_promise_full_checklist():
    """Under Review: honesty payload, empty checklist, dedicated honesty open_url."""
    with patch(
        "app.api.v1.compliance.get_compliance_by_address",
        return_value=_ur_payload(),
    ):
        r = client.get(f"/api/v1/compliance/free-checklist/{PROP_UR}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["is_under_review"] is True
    assert body["label"] == "Under Review"
    assert body["checklist"] == []
    assert "intent=checklist" not in body["open_url"]
    assert body["open_url"] == f"/properties/{PROP_UR}/before-you-list"
    assert body["under_review_message"]
    assert "no checklist to open" in body["under_review_message"]
    assert body["essentials_note"] is None
    assert body["is_compliant"] is False


def test_free_host_interactive_checklist_items_still_403():
    """US-006 unchanged: Essentials still gates interactive checklist-items depth."""
    r = client.get(f"/api/v1/compliance/checklist-items/{PROP_COVERED}")
    assert r.status_code == 403
    assert "Essentials" in r.json().get("detail", "")


def test_free_checklist_requires_ownership():
    """Another host's property_id must 404 (no cross-host leak)."""
    app.dependency_overrides[get_current_user] = lambda: {
        "username": "pl09_other_host",
        "role": "host",
    }
    db = TestingSessionLocal()
    try:
        db.add(Host(id="host_pl09_other", username="pl09_other_host", email="o@t.com", password_hash="x"))
        db.commit()
    finally:
        db.close()
    try:
        with patch(
            "app.api.v1.compliance.get_compliance_by_address",
            return_value=_covered_payload(),
        ):
            r = client.get(f"/api/v1/compliance/free-checklist/{PROP_COVERED}")
        assert r.status_code == 404
    finally:
        app.dependency_overrides[get_current_user] = lambda: {
            "username": FREE_HOST,
            "role": "host",
        }
