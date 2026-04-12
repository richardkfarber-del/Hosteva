from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.worker import redis_client

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

class SubscriptionRequest(BaseModel):
    tier: str

@router.post("/checkout")
async def create_checkout_session(request: SubscriptionRequest):
    """
    Mock Stripe checkout session endpoint.
    TKT-101
    """
    tier_lower = request.tier.lower()
    if tier_lower not in ["basic", "pro"]:
        raise HTTPException(status_code=400, detail="Invalid tier selected")
    
    # Dummy DB update for provider_customer_id
    mock_db_user = {"provider_customer_id": None}
    mock_db_user["provider_customer_id"] = "cus_mock12345"
    
    # Trigger async Redis PDF generation task
    await redis_client.enqueue("generate_document", {"property_id": "mock_property", "tenant_id": "mock_tenant"})
    
    return {
        "status": "pending",
        "checkout_url": f"https://mock-stripe.com/checkout/session_12345?tier={request.tier}",
        "message": "Transaction initiated, awaiting asynchronous payment confirmation.",
        "provider_customer_id": mock_db_user["provider_customer_id"]
    }
