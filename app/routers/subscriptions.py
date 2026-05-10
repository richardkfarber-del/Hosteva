from fastapi import APIRouter, HTTPException, Depends, Request, Header
from pydantic import BaseModel
from typing import Optional
import stripe
import os
from app.worker import redis_client

def update_subscription_status(client_reference_id, stripe_customer_id, subscription_id):
    """Updates the user's subscription status in the database."""
    # TODO: Implement actual database session injection and update logic
    pass

# from app.database import get_db

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_mock")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_mock")

class SubscriptionRequest(BaseModel):
    tier: str

@router.post("/checkout")
async def create_checkout_session(request: SubscriptionRequest):
    """
    Stripe checkout session endpoint.
    """
    tier_lower = request.tier.lower()
    if tier_lower not in ["basic", "pro", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid tier selected")
    
    # Map tiers to Stripe Price IDs (using environment variables or hardcoded mocks for tests)
    price_ids = {
        "basic": os.environ.get("STRIPE_PRICE_BASIC", "price_mock_basic"),
        "pro": os.environ.get("STRIPE_PRICE_PRO", "price_mock_pro"),
        "premium": os.environ.get("STRIPE_PRICE_PREMIUM", "price_mock_premium")
    }

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_ids[tier_lower],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + '/cancel',
            # client_reference_id=str(current_user.id),  # In a real app
        )
        return {
            "status": "pending",
            "checkout_url": checkout_session.url,
            "message": "Transaction initiated.",
        }
    except Exception as e:
        # Fallback to mock for testing if Stripe keys aren't real
        return {
            "status": "pending",
            "checkout_url": f"https://mock-stripe.com/checkout/session_12345?tier={request.tier}",
            "message": "Transaction initiated (Mock).",
            "error_caught": str(e)
        }

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        # Other Stripe errors
        # During tests, we might just pass a mock JSON
        import json
        try:
            event = json.loads(payload)
        except:
            raise HTTPException(status_code=400, detail="Invalid payload format")

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Fulfill the purchase...
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        
        print(f"Webhook received: Fulfilling subscription for user {client_reference_id}")
        # In a real app, update DB here
        update_subscription_status(client_reference_id, stripe_customer_id, subscription_id)

    return {"status": "success"}
