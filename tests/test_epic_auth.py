"""EPIC-AUTH: US-012 register policy, US-013 change-password, US-014 token hash path."""
import hashlib
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_epic_auth.db")
os.environ.setdefault("INTERNAL_DATABASE_URL", "sqlite:///./test_epic_auth.db")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("BILLING_ENABLED", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-epic-auth")
os.environ.setdefault("EMAIL_SINK", "log")
os.environ.pop("EMAIL_FROM", None)
os.environ.pop("RESEND_FROM", None)
os.environ.pop("APP_BASE_URL", None)
os.environ.pop("RESEND_API_KEY", None)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.host import Host
from app.models.password_reset import PasswordResetToken
from app.core.security import get_password_hash, create_access_token, verify_password
from app.services.password_reset import hash_reset_token, issue_reset_for_host
from app.services.email_resend import get_email_from, get_app_base_url, GENERIC_RESET_OK

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    prev = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    yield
    if prev is not None:
        app.dependency_overrides[get_db] = prev
    else:
        app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _seed_host(username="auth_host", email="auth@example.com", password="oldpass12"):
    db = TestingSessionLocal()
    try:
        host = Host(
            id="host_epic_auth",
            username=username,
            email=email,
            password_hash=get_password_hash(password),
        )
        db.add(host)
        db.commit()
        db.refresh(host)
        return host.id
    finally:
        db.close()


def test_email_from_and_base_url_not_hardcoded():
    assert get_email_from() is None
    assert get_app_base_url() is None


def test_register_rejects_digits_only_and_short():
    for pw in ("1234", "12345678", "short"):
        r = client.post(
            "/api/user/register",
            json={"username": f"u_{pw}", "email": f"{pw}@ex.com", "password": pw},
        )
        assert r.status_code == 400, r.text
        body = r.text
        assert pw not in body


def test_register_accepts_policy_password():
    r = client.post(
        "/api/user/register",
        json={"username": "goodhost", "email": "Good.Host@Example.com", "password": "password1"},
    )
    assert r.status_code == 200, r.text
    db = TestingSessionLocal()
    try:
        host = db.query(Host).filter(Host.username == "goodhost").first()
        assert host is not None
        assert host.email == "good.host@example.com"
        assert verify_password("password1", host.password_hash)
        assert host.password_hash != "password1"
    finally:
        db.close()


def test_change_password_unauth_401():
    r = client.post(
        "/api/v1/users/me/password",
        json={"current_password": "x", "new_password": "password1", "confirm_password": "password1"},
    )
    assert r.status_code == 401


def test_change_password_wrong_current_and_weak_new():
    _seed_host()
    token = create_access_token(data={"sub": "auth_host", "role": "host"})
    headers = {"Authorization": f"Bearer {token}"}
    wrong = client.post(
        "/api/v1/users/me/password",
        headers=headers,
        json={"current_password": "nope1234", "new_password": "newpass99", "confirm_password": "newpass99"},
    )
    assert wrong.status_code == 401
    assert wrong.json()["detail"] == "Current password is incorrect"
    db = TestingSessionLocal()
    try:
        host = db.query(Host).filter(Host.username == "auth_host").first()
        assert verify_password("oldpass12", host.password_hash)
    finally:
        db.close()

    weak = client.post(
        "/api/v1/users/me/password",
        headers=headers,
        json={"current_password": "oldpass12", "new_password": "12345678", "confirm_password": "12345678"},
    )
    assert weak.status_code == 400
    assert "12345678" not in weak.text


def test_change_password_success():
    _seed_host()
    token = create_access_token(data={"sub": "auth_host", "role": "host"})
    r = client.post(
        "/api/v1/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "oldpass12", "new_password": "newpass99", "confirm_password": "newpass99"},
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True}
    db = TestingSessionLocal()
    try:
        host = db.query(Host).filter(Host.username == "auth_host").first()
        assert verify_password("newpass99", host.password_hash)
        assert not verify_password("oldpass12", host.password_hash)
    finally:
        db.close()


def test_forgot_request_anti_enumeration_and_token_hash():
    _seed_host()
    captured = {}

    def _capture(to_email, raw_token):
        captured["email"] = to_email
        captured["token"] = raw_token
        return True

    with patch("app.services.password_reset.send_password_reset_email", side_effect=_capture):
        unknown = client.post("/api/v1/users/password-reset/request", json={"email": "nobody@example.com"})
        known = client.post("/api/v1/users/password-reset/request", json={"email": "auth@example.com"})

    assert unknown.status_code == 200
    assert known.status_code == 200
    assert unknown.json()["message"] == known.json()["message"] == GENERIC_RESET_OK
    assert "token" in captured
    raw = captured["token"]
    assert len(raw) >= 32
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    assert hash_reset_token(raw) == digest
    db = TestingSessionLocal()
    try:
        rows = db.query(PasswordResetToken).all()
        assert len(rows) == 1
        assert rows[0].token_hash == digest
        assert raw not in rows[0].token_hash
        assert rows[0].used_at is None
    finally:
        db.close()


def test_reset_confirm_single_use_and_policy():
    _seed_host()
    db = TestingSessionLocal()
    try:
        host = db.query(Host).filter(Host.username == "auth_host").first()
        raw = issue_reset_for_host(db, host)
    finally:
        db.close()

    weak = client.post(
        "/api/v1/users/password-reset/confirm",
        json={"token": raw, "new_password": "1234", "confirm_password": "1234"},
    )
    assert weak.status_code == 400

    ok = client.post(
        "/api/v1/users/password-reset/confirm",
        json={"token": raw, "new_password": "resetpass1", "confirm_password": "resetpass1"},
    )
    assert ok.status_code == 200
    assert ok.json() == {"ok": True}

    reuse = client.post(
        "/api/v1/users/password-reset/confirm",
        json={"token": raw, "new_password": "resetpass2", "confirm_password": "resetpass2"},
    )
    assert reuse.status_code == 400

    db = TestingSessionLocal()
    try:
        host = db.query(Host).filter(Host.username == "auth_host").first()
        assert verify_password("resetpass1", host.password_hash)
        row = db.query(PasswordResetToken).one()
        assert row.used_at is not None
    finally:
        db.close()


def test_reset_confirm_expired_token():
    _seed_host()
    db = TestingSessionLocal()
    try:
        host = db.query(Host).filter(Host.username == "auth_host").first()
        raw = issue_reset_for_host(db, host)
        row = db.query(PasswordResetToken).one()
        row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()
    r = client.post(
        "/api/v1/users/password-reset/confirm",
        json={"token": raw, "new_password": "resetpass1", "confirm_password": "resetpass1"},
    )
    assert r.status_code == 400
    db = TestingSessionLocal()
    try:
        host = db.query(Host).filter(Host.username == "auth_host").first()
        assert verify_password("oldpass12", host.password_hash)
    finally:
        db.close()


def test_auth_pages_and_login_forgot_href():
    assert client.get("/forgot-password").status_code == 200
    assert client.get("/reset-password").status_code == 200
    login = client.get("/login")
    assert login.status_code == 200
    assert 'href="/forgot-password"' in login.text
    assert "Forgot Password?" in login.text
    settings_unauth = client.get("/settings", follow_redirects=False)
    assert settings_unauth.status_code in (303, 307, 302)
    assert "/login" in settings_unauth.headers.get("location", "")
