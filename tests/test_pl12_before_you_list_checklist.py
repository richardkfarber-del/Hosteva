"""PL-12 / US-019 + TE-012 — Before You List interactive checklist.

Guards:
- Free Covered: GET before-you-list 200 with items; PATCH toggle persists + score changes
- Free Covered not 403 on before-you-list APIs (US-006 carve-out)
- Free still 403 on Essentials-only checklist-items (over-broad carve-out guard)
- Under Review: honesty / no fabricated interactive items
- Essentials Covered: interactive path works
- Dedicated page route + dashboard CTA markers (not wizard dead-end)
"""
import os
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite:///./test_pl12_before_you_list.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_pl12_before_you_list.db"
os.environ["BILLING_ENABLED"] = "false"
os.environ["ENVIRONMENT"] = "test"
os.environ.setdefault("JWT_SECRET_KEY", "test-pl12-byl")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.models.before_you_list import BeforeYouListItem  # noqa: F401 — register metadata
from app.db_models import Subscription
from app.core.security import get_current_user

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = (REPO_ROOT / "app" / "templates" / "dashboard.html").read_text()
BYL_PAGE = (REPO_ROOT / "app" / "templates" / "before_you_list.html").read_text()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pl12_before_you_list.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

FREE_HOST = "pl12_free_host"
PAID_HOST = "pl12_paid_host"
HOST_FREE = "host_pl12_free"
HOST_PAID = "host_pl12_paid"
PROP_COVERED = "prop_pl12_covered"
PROP_UR = "prop_pl12_ur"
PROP_PAID = "prop_pl12_paid"


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
        db.add(Host(id=HOST_FREE, username=FREE_HOST, email="pl12free@test.com", password_hash="x"))
        db.add(Host(id=HOST_PAID, username=PAID_HOST, email="pl12paid@test.com", password_hash="x"))
        db.add(Property(
            id=PROP_COVERED,
            user_id=HOST_FREE,
            address="10703 Oak Drive",
            city="Hudson",
            state="FL",
            zip_code="34667",
            property_type="House",
            zoning_status="Action Required",
        ))
        db.add(Property(
            id=PROP_UR,
            user_id=HOST_FREE,
            address="100 Main St",
            city="Brooksville",
            state="FL",
            zip_code="34601",
            property_type="House",
            zoning_status="Pending",
        ))
        db.add(Property(
            id=PROP_PAID,
            user_id=HOST_PAID,
            address="200 Bayshore Blvd",
            city="Tampa",
            state="FL",
            zip_code="33602",
            property_type="Condo",
            zoning_status="Action Required",
        ))
        db.add(Subscription(
            user_id=HOST_PAID,
            status="active",
            tier="ESSENTIALS",
            plan_details="Compliance Essentials",
            stripe_subscription_id="sub_pl12_seed",
            stripe_customer_id="cus_pl12_seed",
        ))
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_pl12_before_you_list.db"):
        os.remove("test_pl12_before_you_list.db")


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
                {"task_name": "Should not appear", "status": "PENDING", "is_compliant": False},
            ],
        }
    )


def test_dashboard_and_page_route_to_dedicated_checklist():
    assert "/properties/" in DASHBOARD and "before-you-list" in DASHBOARD
    assert "buildBeforeYouListUrl" in DASHBOARD
    assert "Before you list" in DASHBOARD
    assert "/api/v1/compliance/before-you-list/" in DASHBOARD
    assert "Official info" in BYL_PAGE
    assert "Compliance progress" in BYL_PAGE
    assert "No full checklist for this address yet" in BYL_PAGE
    assert "Saved — progress updated." in BYL_PAGE
    res = client.get(f"/properties/{PROP_COVERED}/before-you-list")
    # Cookie auth may redirect; route must exist (not 404)
    assert res.status_code in (200, 302, 303, 401, 403)


def test_free_covered_get_before_you_list_200_with_items():
    with patch(
        "app.api.v1.compliance.get_compliance_by_address",
        return_value=_covered_payload(),
    ):
        r = client.get(f"/api/v1/compliance/before-you-list/{PROP_COVERED}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["is_under_review"] is False
    assert body["mode"] == "interactive"
    assert len(body["items"]) >= 2
    assert body["items"][0]["title"] == "Pasco Conditional Use Permit"
    assert body["items"][0]["source_url"] == "https://www.pascocountyfl.gov/"
    assert body["items"][0]["is_complete"] is False
    assert body["compliance_score"] == 0.0
    assert "Research only" in body["honesty"]
    assert "Your checklist for" in body["title"]


def test_free_covered_patch_toggle_persists_and_score_changes():
    with patch(
        "app.api.v1.compliance.get_compliance_by_address",
        return_value=_covered_payload(),
    ):
        r0 = client.get(f"/api/v1/compliance/before-you-list/{PROP_COVERED}")
    assert r0.status_code == 200
    items = r0.json()["items"]
    item_id = items[0]["id"]
    assert r0.json()["compliance_score"] == 0.0

    r1 = client.patch(
        f"/api/v1/compliance/before-you-list/{PROP_COVERED}/items/{item_id}",
        json={"is_complete": True},
    )
    assert r1.status_code == 200, r1.text
    body1 = r1.json()
    assert body1["item"]["is_complete"] is True
    assert body1["compliance_score"] > 0
    expected = round((1 / len(items)) * 100.0, 1)
    assert body1["compliance_score"] == expected
    assert "Saved" in body1["toast"]

    with patch(
        "app.api.v1.compliance.get_compliance_by_address",
        return_value=_covered_payload(),
    ):
        r2 = client.get(f"/api/v1/compliance/before-you-list/{PROP_COVERED}")
    assert r2.status_code == 200
    reloaded = {i["id"]: i for i in r2.json()["items"]}
    assert reloaded[item_id]["is_complete"] is True
    assert r2.json()["compliance_score"] == expected

    r3 = client.patch(
        f"/api/v1/compliance/before-you-list/{PROP_COVERED}/items/{item_id}",
        json={"is_complete": False},
    )
    assert r3.status_code == 200
    assert r3.json()["item"]["is_complete"] is False
    assert r3.json()["compliance_score"] == 0.0


def test_free_covered_not_403_on_before_you_list_apis():
    with patch(
        "app.api.v1.compliance.get_compliance_by_address",
        return_value=_covered_payload(),
    ):
        g = client.get(f"/api/v1/compliance/before-you-list/{PROP_COVERED}")
    assert g.status_code == 200
    item_id = g.json()["items"][0]["id"]
    p = client.patch(
        f"/api/v1/compliance/before-you-list/{PROP_COVERED}/items/{item_id}",
        json={"is_complete": True},
    )
    assert p.status_code == 200
    assert p.status_code != 403


def test_free_still_403_on_essentials_checklist_items():
    """Over-broad carve-out guard: legacy Essentials API stays gated."""
    r = client.get(f"/api/v1/compliance/checklist-items/{PROP_COVERED}")
    assert r.status_code == 403
    assert "Essentials" in r.json().get("detail", "")


def test_under_review_honesty_no_fabricated_items():
    with patch(
        "app.api.v1.compliance.get_compliance_by_address",
        return_value=_ur_payload(),
    ):
        r = client.get(f"/api/v1/compliance/before-you-list/{PROP_UR}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["is_under_review"] is True
    assert body["mode"] == "honesty"
    assert body["items"] == []
    assert body["compliance_score"] is None
    assert "No full checklist" in body["headline"]
    assert "won't invent" in body["body"]
    assert body["honesty"]


def test_essentials_covered_interactive_path_works():
    app.dependency_overrides[get_current_user] = lambda: {"username": PAID_HOST, "role": "host"}
    try:
        with patch(
            "app.api.v1.compliance.get_compliance_by_address",
            return_value=_covered_payload(),
        ):
            r = client.get(f"/api/v1/compliance/before-you-list/{PROP_PAID}")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["mode"] == "interactive"
        assert len(body["items"]) >= 1
        item_id = body["items"][0]["id"]
        p = client.patch(
            f"/api/v1/compliance/before-you-list/{PROP_PAID}/items/{item_id}",
            json={"is_complete": True},
        )
        assert p.status_code == 200
        assert p.json()["item"]["is_complete"] is True
        assert p.json()["compliance_score"] > 0
    finally:
        app.dependency_overrides[get_current_user] = lambda: {
            "username": FREE_HOST,
            "role": "host",
        }


def test_free_checklist_open_url_points_to_dedicated_page():
    with patch(
        "app.api.v1.compliance.get_compliance_by_address",
        return_value=_covered_payload(),
    ):
        r = client.get(f"/api/v1/compliance/free-checklist/{PROP_COVERED}")
    assert r.status_code == 200
    assert r.json()["open_url"] == f"/properties/{PROP_COVERED}/before-you-list"
    assert "intent=checklist" not in r.json()["open_url"]
