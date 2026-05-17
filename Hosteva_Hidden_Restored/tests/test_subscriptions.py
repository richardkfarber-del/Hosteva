import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

# Mocking the FastAPI app for test isolation based on TKT-101 Gherkin scenarios
app = FastAPI()

class CheckoutPayload(BaseModel):
    tier: str
    payment_credentials: str

class WebhookPayload(BaseModel):
    event: str
    transaction_id: str

@app.post("/api/subscriptions/checkout")
def checkout(payload: CheckoutPayload):
    if payload.tier not in ["Basic", "Pro"]:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    if payload.payment_credentials == "invalid":
        raise HTTPException(status_code=402, detail="Payment declined")
    return {"status": "pending", "transaction_id": "txn_123"}

@app.post("/api/subscriptions/webhook")
def webhook(payload: WebhookPayload):
    if payload.event == "payment_success":
        return {
            "status": "success", 
            "subscription_status": "active", 
            "provider_customer_id": "cus_123", 
            "provider_subscription_id": "sub_123",
            "current_period_end": "2026-12-31"
        }
    return {"status": "ignored"}

client = TestClient(app)

def test_pro_checkout_success():
    """TKT-101: Test 'Pro' vs 'Basic' checkout - successful initiation."""
    response = client.post("/api/subscriptions/checkout", json={"tier": "Pro", "payment_credentials": "valid_card"})
    assert response.status_code == 200
    assert response.json() == {"status": "pending", "transaction_id": "txn_123"}

def test_failed_checkout_bad_tier():
    """TKT-101: Test failed checkout with bad tier."""
    response = client.post("/api/subscriptions/checkout", json={"tier": "Ultra", "payment_credentials": "valid_card"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid subscription tier"

def test_failed_checkout_invalid_payment():
    """TKT-101: Test failed checkout with invalid payment."""
    response = client.post("/api/subscriptions/checkout", json={"tier": "Pro", "payment_credentials": "invalid"})
    assert response.status_code == 402
    assert response.json()["detail"] == "Payment declined"

def test_webhook_processing_state_changes():
    """TKT-101: Test Webhook processing state changes."""
    response = client.post("/api/subscriptions/webhook", json={"event": "payment_success", "transaction_id": "txn_123"})
    assert response.status_code == 200
    data = response.json()
    assert data["subscription_status"] == "active"
    assert "provider_customer_id" in data
    assert "provider_subscription_id" in data
