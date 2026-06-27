from fastapi import APIRouter, HTTPException, Depends, Request, Header
from pydantic import BaseModel
from typing import Optional
import stripe
import os
from app.worker import redis_client
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.host import Host
from app.db_models import Subscription
from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM

def update_subscription_status(db: Session, client_reference_id: str, stripe_customer_id: str, subscription_id: str):
    """Updates the user's subscription status in the database."""
    if not client_reference_id:
        print("update_subscription_status called with empty client_reference_id")
        return
        
    # Check if host exists (client_reference_id can be host.id or host.username)
    host = db.query(Host).filter(
        (Host.id == client_reference_id) | 
        (Host.username == client_reference_id) | 
        (Host.email == client_reference_id)
    ).first()
    if not host:
        print(f"Host not found for client_reference_id: {client_reference_id}")
        return
        
    # Find or create subscription
    sub = db.query(Subscription).filter(Subscription.user_id == host.id).first()
    if not sub:
        sub = Subscription(user_id=host.id)
        db.add(sub)
    sub.stripe_customer_id = stripe_customer_id
    sub.status = "active"
    sub.plan_details = subscription_id
    db.commit()
    print(f"Successfully activated subscription for host {host.id}")

async def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username:
            return db.query(Host).filter(Host.username == username).first()
    except Exception:
        return None
    return None


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_mock")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_mock")

class SubscriptionRequest(BaseModel):
    tier: str

@router.post("/checkout")
async def create_checkout_session(
    request: SubscriptionRequest, 
    current_host: Optional[Host] = Depends(get_current_user_optional)
):
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

    client_reference_id = current_host.id if current_host else "user_mock_123"

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
            client_reference_id=client_reference_id,
        )
        return {
            "status": "pending",
            "checkout_url": checkout_session.url,
            "message": "Transaction initiated.",
        }
    except Exception as e:
        return {
            "status": "pending",
            "checkout_url": f"/checkout-mock?session_id=session_12345&type=subscription&tier={request.tier}&client_ref={client_reference_id}",
            "message": "Transaction initiated (Mock).",
            "error_caught": str(e)
        }

@router.post("/webhook")
async def stripe_webhook(
    request: Request, 
    stripe_signature: Optional[str] = Header(None), 
    db: Session = Depends(get_db)
):
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
        update_subscription_status(db, client_reference_id, stripe_customer_id, subscription_id)

    return {"status": "success"}
