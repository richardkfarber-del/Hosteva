"""BUG_US006: Free checklist-items / tasks must 403, never 500."""
import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///./test_bug_us006_gate.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_bug_us006_gate.db"
os.environ["BILLING_ENABLED"] = "false"
os.environ["ENVIRONMENT"] = "development"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.host import Host
from app.core.security import get_current_user
from app.core import billing_gate
from app.db_models import Subscription

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_bug_us006_gate.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

HOST_ID = "host_bug_us006"
HOST_USERNAME = "bug_free"


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
    app.dependency_overrides[get_current_user] = lambda: {"username": HOST_USERNAME, "role": "host"}
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Create schema + seed host once; drop only after the whole module."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add(Host(id=HOST_ID, username=HOST_USERNAME, email="bug@t.com", password_hash="x"))
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_bug_us006_gate.db"):
        os.remove("test_bug_us006_gate.db")


@pytest.fixture(autouse=True)
def reset_free_host_entitlement(request):
    """Keep free-host cases isolated from simulate mutations."""
    if request.node.name == "test_simulate_entitlement_allowed_with_flag":
        yield
        return
    db = TestingSessionLocal()
    try:
        sub = db.query(Subscription).filter(Subscription.user_id == HOST_ID).first()
        if sub:
            db.delete(sub)
            db.commit()
    finally:
        db.close()
    yield


client = TestClient(app)


def test_free_checklist_items_403_not_500():
    r = client.get(f"/api/v1/compliance/checklist-items/{uuid.uuid4()}")
    assert r.status_code == 403, r.text
    assert "Essentials" in r.json().get("detail", "")


def test_free_tasks_403_not_500():
    r = client.get(f"/api/v1/compliance/tasks/{uuid.uuid4()}")
    assert r.status_code == 403, r.text
    assert "Essentials" in r.json().get("detail", "")


def test_relationship_boom_still_403(monkeypatch):
    """Lazy-load failures must not become 500."""
    def boom(*a, **k):
        raise RuntimeError("simulated relationship failure")

    monkeypatch.setattr(billing_gate, "get_host_subscription", boom)
    # host_has_active_essentials catches and returns False → 403
    r = client.get(f"/api/v1/compliance/checklist-items/{uuid.uuid4()}")
    assert r.status_code == 403, r.text


def test_simulate_entitlement_allowed_with_flag(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ALLOW_BILLING_SIMULATION", "true")
    # Re-import path uses os.getenv at call time for allow flag
    r = client.post("/api/v1/billing/simulate-entitlement")
    assert r.status_code == 200, r.text
    assert r.json().get("has_active_subscription") is True
    # now checklist should pass entitlement (may 200 empty list)
    r2 = client.get(f"/api/v1/compliance/checklist-items/{uuid.uuid4()}")
    assert r2.status_code == 200, r2.text
