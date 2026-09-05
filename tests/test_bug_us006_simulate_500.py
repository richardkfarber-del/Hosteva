"""BUG_US006_SIMULATE_500: simulate-entitlement must 200 when ALLOW_BILLING_SIMULATION=true."""
import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///./test_bug_us006_sim.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_bug_us006_sim.db"
os.environ["BILLING_ENABLED"] = "false"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_for_us006_sim"
os.environ["STRIPE_SECRET_KEY"] = "sk_live_test_dummy_key_for_unit_tests"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_dummy"
# Do not set ENVIRONMENT=production at import (poisons IS_PRODUCTION / HTTPS middleware
# for sibling test modules). Production+ALLOW path is monkeypatched per-test below.
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, SessionLocal
from app.main import app
from app.models.host import Host
from app.core.security import get_current_user
import app.api.v1.billing as billing_mod

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_bug_us006_sim.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Simulate legacy DB: drop tier column if we can recreate without it — skip;
    # instead create host and run simulate which must succeed even if tier added later.
    SessionLocal.configure(bind=engine)
    db = TestingSessionLocal()
    db.add(Host(id="host_sim_500", username="sim_free", email="sim@t.com", password_hash="x"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_bug_us006_sim.db"):
        os.remove("test_bug_us006_sim.db")


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def overrides(monkeypatch):
    # Live probe scenario: production + ALLOW_BILLING_SIMULATION + live-shaped secrets
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ALLOW_BILLING_SIMULATION", "true")
    monkeypatch.setattr(billing_mod, "IS_PRODUCTION", True)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: {"username": "sim_free", "role": "host"}
    yield
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


client = TestClient(app)


def test_simulate_entitlement_200_with_flag():
    r = client.post("/api/v1/billing/simulate-entitlement")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("has_active_subscription") is True
    assert "Essentials" in data.get("tier", "")


def test_me_and_checklist_after_simulate():
    r = client.post("/api/v1/billing/simulate-entitlement")
    assert r.status_code == 200, r.text
    me = client.get("/api/v1/users/me")
    assert me.status_code == 200
    body = me.json()
    assert body.get("has_active_subscription") is True
    r2 = client.get(f"/api/v1/compliance/checklist-items/{uuid.uuid4()}")
    assert r2.status_code == 200, r2.text
