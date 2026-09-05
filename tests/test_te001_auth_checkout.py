"""TE-001: Auth-bound Stripe checkout — never user_mock_123."""
import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_te001_auth_checkout.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_te001_auth_checkout.db"
os.environ["BILLING_ENABLED"] = "true"

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.host import Host
from app.core.security import get_current_user

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_te001_auth_checkout.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    original_override = fastapi_app.dependency_overrides.get(get_db)
    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield
    if original_override is not None:
        fastapi_app.dependency_overrides[get_db] = original_override
    else:
        fastapi_app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        host = Host(
            id="host_billing_test",
            username="billing_host",
            email="billing@hosteva.com",
            password_hash="mocked_hash",
        )
        db.add(host)
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_te001_auth_checkout.db"):
        os.remove("test_te001_auth_checkout.db")


client = TestClient(fastapi_app)


def override_get_current_user():
    return {"username": "billing_host", "role": "host"}


@pytest.fixture
def auth_header():
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_user
    yield {"Authorization": "Bearer fake_token"}
    fastapi_app.dependency_overrides.pop(get_current_user, None)


CHECKOUT_PATHS = (
    "/api/v1/billing/checkout",
    "/api/subscriptions/checkout",
)


@pytest.mark.parametrize("path", CHECKOUT_PATHS)
def test_unauth_checkout_returns_401_no_session_create(path, monkeypatch):
    monkeypatch.setenv("BILLING_ENABLED", "true")
    fastapi_app.dependency_overrides.pop(get_current_user, None)
    with patch("stripe.checkout.Session.create") as mock_create:
        response = client.post(path, json={"tier": "ESSENTIALS", "interval": "monthly"})
        assert response.status_code == 401
        mock_create.assert_not_called()


@pytest.mark.parametrize("path", CHECKOUT_PATHS)
def test_auth_checkout_uses_real_host_id(path, auth_header, monkeypatch):
    monkeypatch.setenv("BILLING_ENABLED", "true")
    with patch("stripe.checkout.Session.create") as mock_create:
        mock_session = MagicMock()
        mock_session.id = "cs_te001_auth"
        mock_session.url = "https://checkout.stripe.com/pay/cs_te001_auth"
        mock_create.return_value = mock_session

        payload = {"tier": "ESSENTIALS", "interval": "monthly"}
        if path.endswith("/subscriptions/checkout"):
            payload = {"tier": "pro"}

        response = client.post(path, json=payload, headers=auth_header)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get("client_reference_id") == "host_billing_test"
        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        assert kwargs.get("client_reference_id") == "host_billing_test"
        assert "user_mock_123" not in str(kwargs)
        assert "user_mock_123" not in str(mock_create.call_args)
        assert kwargs.get("metadata", {}).get("tier") == "ESSENTIALS"
        assert kwargs.get("metadata", {}).get("host_id") == "host_billing_test"


def test_auth_kill_switch_503_before_session_create(auth_header, monkeypatch):
    monkeypatch.setenv("BILLING_ENABLED", "false")
    with patch("stripe.checkout.Session.create") as mock_create:
        for path, payload in (
            ("/api/subscriptions/checkout", {"tier": "basic"}),
            ("/api/v1/billing/checkout", {"tier": "ESSENTIALS", "interval": "monthly"}),
        ):
            response = client.post(path, json=payload, headers=auth_header)
            assert response.status_code == 503
            assert "Billing temporarily unavailable" in response.json().get("detail", "")
        mock_create.assert_not_called()
