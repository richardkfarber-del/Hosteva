import pytest
import stripe
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

client = TestClient(app)

def test_create_checkout_session():
    response = client.post("/api/stripe/create-checkout-session")
    assert response.status_code == 200
    assert "url" in response.json()

def test_stripe_webhook_no_signature():
    response = client.post("/api/stripe/webhook", json={"type": "checkout.session.completed"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid signature"}

@patch('stripe.Webhook.construct_event')
def test_stripe_webhook_with_signature(mock_construct_event):
    mock_construct_event.return_value = {
        'type': 'checkout.session.completed'
    }
    
    # Mock get_db
    class MockDB:
        def query(self, *args, **kwargs):
            return self
        def first(self):
            class MockHost:
                subscription_tier = "free"
            return MockHost()
        def commit(self):
            pass
            
    app.dependency_overrides[get_db] = lambda: MockDB()
    
    response = client.post(
        "/api/stripe/webhook", 
        json={"type": "checkout.session.completed"},
        headers={"Stripe-Signature": "t=123,v1=abc"}
    )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_rag_query_forbidden_if_not_premium():
    response = client.post(
        "/api/compliance/rag/query",
        json={"query": "test query", "address": "test address"}
    )
    # Our mock implementation returns 403 Forbidden for non-premium
    assert response.status_code == 403
    assert "Premium subscription required" in response.json()["detail"]
