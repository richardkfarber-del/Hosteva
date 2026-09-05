import pytest
import uuid
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Force SQLite test URL globally
os.environ["DATABASE_URL"] = "sqlite:///./test_billing_v1.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_billing_v1.db"
# Success-path checkout tests opt in; kill-switch defaults OFF in prod.
os.environ["BILLING_ENABLED"] = "true"

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.host import Host
from app.models.property import Property
from app.models.compliance import MunicipalCode, PropertyCompliance
from app.db_models import Subscription, PermitTransaction

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_billing_v1.db"
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
        # Create a test host
        host = Host(
            id="host_billing_test",
            username="billing_host",
            email="billing@hosteva.com",
            password_hash="mocked_hash"
        )
        db.add(host)
        
        # Create a test property
        prop = Property(
            id="property_billing_test",
            user_id="host_billing_test",
            address="456 Beach Ave",
            city="Miami Beach",
            state="FL",
            zip_code="33139",
            property_type="Condo"
        )
        db.add(prop)
        
        # Create a compliance task that represents the permit
        mc = MunicipalCode(
            id=uuid.UUID("22222222-3333-4444-5555-66666666666f"),
            municipality_name="Miami Beach",
            ordinance_number="MB-STR-1",
            requires_permit=True,
            permit_name="Miami Beach STR Permit"
        )
        db.add(mc)
        
        task = PropertyCompliance(
            id=uuid.UUID("abcdef12-1234-5678-90ab-cdef12345678"),
            property_id="property_billing_test",
            municipal_code_id=uuid.UUID("22222222-3333-4444-5555-66666666666f"),
            is_compliant=False,
            status="PENDING",
            task_name="STR Permit Application",
            valid_period="[2026-06-04 00:00:00, 2027-06-04 00:00:00]"
        )
        db.add(task)
        
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_billing_v1.db"):
        os.remove("test_billing_v1.db")

client = TestClient(fastapi_app)

from app.core.security import get_current_user

def override_get_current_user():
    return {"username": "billing_host", "role": "host"}

# Helper for authenticated tests
@pytest.fixture
def auth_header():
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_user
    yield {"Authorization": "Bearer fake_token"}
    fastapi_app.dependency_overrides.pop(get_current_user, None)


def test_checkout_unauthorized():
    response = client.post("/api/v1/billing/checkout", json={"tier": "STARTER"})
    assert response.status_code == 401

def test_checkout_kill_switch_off_returns_503(auth_header, monkeypatch):
    """Unauth → 401 (auth first). Auth + BILLING_ENABLED=false → 503, no Session.create."""
    monkeypatch.setenv("BILLING_ENABLED", "false")
    # Ensure unauth path: clear any leftover auth override for this call
    fastapi_app.dependency_overrides.pop(get_current_user, None)
    with patch("stripe.checkout.Session.create") as mock_session_create:
        unauth = client.post(
            "/api/subscriptions/checkout",
            json={"tier": "pro"},
        )
        assert unauth.status_code == 401
        mock_session_create.assert_not_called()

        # Re-apply auth override for authenticated kill-switch checks
        fastapi_app.dependency_overrides[get_current_user] = override_get_current_user

        response = client.post(
            "/api/subscriptions/checkout",
            json={"tier": "pro"},
            headers=auth_header,
        )
        assert response.status_code == 503
        assert "Billing temporarily unavailable" in response.json().get("detail", "")
        mock_session_create.assert_not_called()

        response2 = client.post(
            "/api/v1/billing/checkout",
            json={"tier": "STARTER"},
            headers=auth_header,
        )
        assert response2.status_code == 503
        mock_session_create.assert_not_called()


def test_checkout_subscription_success(auth_header, monkeypatch):
    monkeypatch.setenv("BILLING_ENABLED", "true")
    # Mock stripe session creation
    with patch("stripe.checkout.Session.create") as mock_session_create:
        mock_session = MagicMock()
        mock_session.id = "cs_test_sub_123"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_sub_123"
        mock_session_create.return_value = mock_session
        
        response = client.post(
            "/api/v1/billing/checkout",
            json={"tier": "STARTER"},
            headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "cs_test_sub_123"
        assert "checkout_url" in data
        assert data.get("client_reference_id") == "host_billing_test"
        mock_session_create.assert_called_once()
        kwargs = mock_session_create.call_args.kwargs
        assert kwargs.get("client_reference_id") == "host_billing_test"
        assert "user_mock_123" not in str(kwargs)
        assert kwargs.get("metadata", {}).get("tier") == "ESSENTIALS"

def test_checkout_permit_filing_success(auth_header, monkeypatch):
    monkeypatch.setenv("BILLING_ENABLED", "true")
    with patch("stripe.checkout.Session.create") as mock_session_create:
        mock_session = MagicMock()
        mock_session.id = "cs_test_permit_123"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_permit_123"
        mock_session_create.return_value = mock_session
        
        response = client.post(
            "/api/v1/billing/checkout",
            json={"tier": "PERMIT_FILING", "property_id": "property_billing_test"},
            headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "cs_test_permit_123"
        
        # Verify PermitTransaction record was created in database
        db = TestingSessionLocal()
        tx = db.query(PermitTransaction).filter(PermitTransaction.stripe_session_id == "cs_test_permit_123").first()
        assert tx is not None
        assert tx.property_id == "property_billing_test"
        assert tx.payment_status == "PENDING"
        db.close()

def test_webhook_subscription_completed():
    payload = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_sub_completed",
                "mode": "subscription",
                "client_reference_id": "host_billing_test",
                "customer": "cus_billing_test",
                "subscription": "sub_billing_test",
                "metadata": {
                    "type": "subscription",
                    "tier": "GROWTH"
                }
            }
        }
    }
    
    response = client.post(
        "/api/v1/billing/webhooks",
        json=payload,
        headers={"stripe-signature": "mock_sig"}
    )
    assert response.status_code == 200
    
    # Verify subscription in database
    db = TestingSessionLocal()
    sub = db.query(Subscription).filter(Subscription.user_id == "host_billing_test").first()
    assert sub is not None
    assert sub.status == "active"
    assert sub.tier == "ESSENTIALS"  # US-006: aliases normalize to ESSENTIALS
    assert sub.stripe_subscription_id == "sub_billing_test"
    db.close()

def test_webhook_permit_completed():
    # First seed a pending transaction
    db = TestingSessionLocal()
    pending_tx = PermitTransaction(
        property_id="property_billing_test",
        stripe_session_id="cs_test_permit_completed",
        payment_status="PENDING",
        amount_paid=150.0
    )
    db.add(pending_tx)
    db.commit()
    db.close()
    
    payload = {
        "id": "evt_test_456",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_permit_completed",
                "mode": "payment",
                "client_reference_id": "host_billing_test",
                "customer": "cus_billing_test",
                "amount_total": 15000,
                "metadata": {
                    "type": "permit_filing",
                    "property_id": "property_billing_test"
                }
            }
        }
    }
    
    response = client.post(
        "/api/v1/billing/webhooks",
        json=payload,
        headers={"stripe-signature": "mock_sig"}
    )
    assert response.status_code == 200
    
    # Verify transaction and compliance approval in database
    db = TestingSessionLocal()
    tx = db.query(PermitTransaction).filter(PermitTransaction.stripe_session_id == "cs_test_permit_completed").first()
    assert tx.payment_status == "PAID"
    
    task = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == "property_billing_test").first()
    assert task.status == "APPROVED"
    assert task.is_compliant is True
    db.close()
