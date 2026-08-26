import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_checkout_session_valid_tier():
    response = client.post("/api/subscriptions/checkout", json={"tier": "pro"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert "checkout_url" in data

def test_checkout_session_invalid_tier():
    response = client.post("/api/subscriptions/checkout", json={"tier": "invalid_tier"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid tier selected"

@patch('stripe.Webhook.construct_event')
@patch('app.routers.subscriptions.update_subscription_status', create=True)
def test_stripe_webhook_database_update(mock_db_update, mock_construct_event):
    """
    Test that the Stripe webhook successfully updates the database.
    """
    payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": "user_123",
                "customer": "cus_123",
                "subscription": "sub_123"
            }
        }
    }
    
    # Bypass Stripe signature verification by mocking the constructed event
    mock_construct_event.return_value = payload
    
    response = client.post("/api/subscriptions/webhook", json=payload)
    assert response.status_code == 200
    
    # Assert that the database update logic was actually triggered
    assert mock_db_update.called, "BUG DETECTED: Webhook fired but database was not updated!"
