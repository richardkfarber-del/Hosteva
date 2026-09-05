"""US-006: Authenticated Essentials entitlement gating + webhook sim."""
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_us006_entitlement.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_us006_entitlement.db"
os.environ["BILLING_ENABLED"] = "false"  # kill-switch stays off; webhook sim does not need it
os.environ["ENVIRONMENT"] = "test"

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.models.compliance import MunicipalCode, PropertyCompliance
from app.db_models import Subscription
from app.core.security import get_current_user

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_us006_entitlement.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

FREE_HOST = "us006_free_host"
PAID_HOST = "us006_paid_host"
PROP_FREE = "prop_us006_free"
PROP_PAID = "prop_us006_paid"
TASK_FREE = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeee1")
TASK_PAID = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeee2")
MC_ID = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeee0")


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
def override_db():
    original = fastapi_app.dependency_overrides.get(get_db)
    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield
    if original is not None:
        fastapi_app.dependency_overrides[get_db] = original
    else:
        fastapi_app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add(Host(id="host_us006_free", username=FREE_HOST, email="free@us006.test", password_hash="x"))
        db.add(Host(id="host_us006_paid", username=PAID_HOST, email="paid@us006.test", password_hash="x"))
        db.add(Property(
            id=PROP_FREE, user_id="host_us006_free", address="1 Free St",
            city="Tampa", state="FL", zip_code="33602", property_type="Condo",
        ))
        db.add(Property(
            id=PROP_PAID, user_id="host_us006_paid", address="2 Paid Ave",
            city="Tampa", state="FL", zip_code="33602", property_type="Condo",
        ))
        db.add(MunicipalCode(
            id=MC_ID, municipality_name="Tampa", ordinance_number="US006-1", requires_permit=True,
        ))
        db.add(PropertyCompliance(
            id=TASK_FREE, property_id=PROP_FREE, municipal_code_id=MC_ID,
            is_compliant=False, status="PENDING", task_name="STR Permit Free",
            valid_period="[2026-01-01 00:00:00, 2027-01-01 00:00:00]",
        ))
        db.add(PropertyCompliance(
            id=TASK_PAID, property_id=PROP_PAID, municipal_code_id=MC_ID,
            is_compliant=False, status="PENDING", task_name="STR Permit Paid",
            valid_period="[2026-01-01 00:00:00, 2027-01-01 00:00:00]",
        ))
        db.add(Subscription(
            user_id="host_us006_paid",
            status="active",
            tier="ESSENTIALS",
            plan_details="Compliance Essentials",
            stripe_subscription_id="sub_us006_seed",
            stripe_customer_id="cus_us006_seed",
        ))
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_us006_entitlement.db"):
        os.remove("test_us006_entitlement.db")


client = TestClient(fastapi_app)


@pytest.fixture(autouse=True)
def reset_free_host_entitlement(request):
    """Keep free-host cases isolated from webhook/simulate mutations."""
    if request.node.name in {
        "test_webhook_sim_activates_essentials_on_me",
        "test_simulate_entitlement_non_prod",
        "test_simulate_entitlement_blocked_in_production",
    }:
        yield
        return
    db = TestingSessionLocal()
    try:
        sub = db.query(Subscription).filter(Subscription.user_id == "host_us006_free").first()
        if sub:
            db.delete(sub)
            db.commit()
    finally:
        db.close()
    yield


@pytest.fixture
def as_free():
    fastapi_app.dependency_overrides[get_current_user] = lambda: {"username": FREE_HOST, "role": "host"}
    yield {"Authorization": "Bearer fake"}
    fastapi_app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def as_paid():
    fastapi_app.dependency_overrides[get_current_user] = lambda: {"username": PAID_HOST, "role": "host"}
    yield {"Authorization": "Bearer fake"}
    fastapi_app.dependency_overrides.pop(get_current_user, None)


def test_free_host_checklist_403(as_free):
    r = client.get(f"/api/v1/compliance/checklist-items/{PROP_FREE}", headers=as_free)
    assert r.status_code == 403
    assert "Essentials" in r.json().get("detail", "")


def test_free_host_task_depth_403(as_free):
    r = client.get(f"/api/v1/compliance/tasks/{TASK_FREE}", headers=as_free)
    assert r.status_code == 403


def test_entitled_host_checklist_ok(as_paid):
    r = client.get(f"/api/v1/compliance/checklist-items/{PROP_PAID}", headers=as_paid)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert items[0]["property_id"] == PROP_PAID


def test_entitled_host_task_depth_ok(as_paid):
    r = client.get(f"/api/v1/compliance/tasks/{TASK_PAID}", headers=as_paid)
    assert r.status_code == 200
    body = r.json()
    assert body["task_name"] == "STR Permit Paid"
    assert "what_to_upload" in body


def test_webhook_sim_activates_essentials_on_me(as_free):
    me = client.get("/api/v1/users/me", headers=as_free)
    assert me.status_code == 200
    assert me.json()["has_active_subscription"] is False
    assert me.json()["tier"] == "Free Tier"

    payload = {
        "id": "evt_us006_1",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_us006_sim",
                "mode": "subscription",
                "client_reference_id": "host_us006_free",
                "customer": "cus_us006_webhook",
                "subscription": "sub_us006_webhook",
                "metadata": {"type": "subscription", "tier": "GROWTH"},
            }
        },
    }
    wr = client.post("/api/v1/billing/webhooks", json=payload, headers={"stripe-signature": "mock"})
    assert wr.status_code == 200

    me2 = client.get("/api/v1/users/me", headers=as_free)
    assert me2.status_code == 200
    body = me2.json()
    assert body["has_active_subscription"] is True
    assert body["tier"] == "Compliance Essentials"
    assert body["subscription_tier"] == "ESSENTIALS"

    cr = client.get(f"/api/v1/compliance/checklist-items/{PROP_FREE}", headers=as_free)
    assert cr.status_code == 200


def test_simulate_entitlement_non_prod(as_free):
    db = TestingSessionLocal()
    sub = db.query(Subscription).filter(Subscription.user_id == "host_us006_free").first()
    if sub:
        sub.status = "inactive"
        sub.tier = "FREE"
        db.commit()
    db.close()

    r = client.post("/api/v1/billing/simulate-entitlement", headers=as_free)
    assert r.status_code == 200
    assert r.json()["has_active_subscription"] is True
    assert r.json()["tier"] == "Compliance Essentials"

    me = client.get("/users/me", headers=as_free)
    assert me.json()["has_active_subscription"] is True
    assert me.json()["tier"] == "Compliance Essentials"


def test_simulate_entitlement_blocked_in_production(as_free, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    import app.api.v1.billing as billing_mod
    monkeypatch.setattr(billing_mod, "IS_PRODUCTION", True)
    r = client.post("/api/v1/billing/simulate-entitlement", headers=as_free)
    assert r.status_code == 404
