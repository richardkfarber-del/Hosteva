"""BUG: /api/user/me must not collapse Bearer hosts into Guest."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_user_me_guest.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_user_me_guest.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-user-me")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.core.security import get_current_user, create_access_token

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Host(id="host_me_fix", username="real_host_me", email="real@host.test", password_hash="x"))
    db.commit()
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    prev_db = app.dependency_overrides.get(get_db)
    prev_user = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_current_user, None)
    if prev_db is not None:
        app.dependency_overrides[get_db] = prev_db
    else:
        app.dependency_overrides.pop(get_db, None)
    if prev_user is not None:
        app.dependency_overrides[get_current_user] = prev_user
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_api_user_me_returns_host_not_guest():
    token = create_access_token(data={"sub": "real_host_me", "role": "host"})
    r = client.get("/api/user/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "real_host_me"
    assert data["username"] != "Guest"
    assert data.get("email") == "real@host.test"
    assert "has_active_subscription" in data
    assert "subscription_tier" in data
    assert "subscription_status" in data
    assert data.get("tier") in ("Free Tier", "Compliance Essentials")


def test_api_user_me_matches_v1_shape_for_host():
    token = create_access_token(data={"sub": "real_host_me", "role": "host"})
    headers = {"Authorization": f"Bearer {token}"}
    legacy = client.get("/api/user/me", headers=headers).json()
    v1 = client.get("/api/v1/users/me", headers=headers).json()
    assert legacy["username"] == v1["username"] == "real_host_me"
    assert legacy["username"] != "Guest"
    assert legacy["has_active_subscription"] == v1["has_active_subscription"]


def test_api_user_me_missing_host_returns_username_not_guest():
    app.dependency_overrides[get_current_user] = lambda: {"sub": "ghost_user_no_row"}
    r = client.get("/api/user/me")
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "ghost_user_no_row"
    assert data["username"] != "Guest"
    assert data["tier"] == "Free Tier"
    assert data["has_active_subscription"] is False
    assert data["subscription_tier"] == "FREE"
