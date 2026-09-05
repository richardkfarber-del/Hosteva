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
from app.core.billing_gate import (
    require_billing_enabled,
    require_checkout_host,
    checkout_client_reference_id,
    resolve_essentials_price_id,
    essentials_checkout_custom_text,
)

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

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
IS_PRODUCTION = os.environ.get("ENVIRONMENT", "").lower() == "production"

if IS_PRODUCTION:
    if not stripe.api_key or stripe.api_key.startswith("sk_test"):
        raise RuntimeError("STRIPE_SECRET_KEY must be a live key in production")
    if not STRIPE_WEBHOOK_SECRET or STRIPE_WEBHOOK_SECRET.startswith("whsec_mock"):
        raise RuntimeError("STRIPE_WEBHOOK_SECRET must be set in production")

class SubscriptionRequest(BaseModel):
    tier: str
    interval: Optional[str] = None  # monthly | yearly

@router.post("/checkout")
async def create_checkout_session(
    request: SubscriptionRequest,
    host: Host = Depends(require_checkout_host),
):
    """
    Auth-bound Stripe checkout. Auth via Depends first; kill-switch before Session.create.
    Phase I: all paid tiers map to Compliance Essentials (monthly or yearly).
    """
    # Auth already enforced by require_checkout_host (401 if missing).
    require_billing_enabled()

    tier_lower = (request.tier or "").lower()
    allowed = {
        "basic", "pro", "premium", "compliance_essentials", "essentials",
        "starter", "growth", "enterprise", "free",
    }
    if tier_lower not in allowed:
        raise HTTPException(status_code=400, detail="Invalid tier selected")

    IS_PRODUCTION = os.environ.get("ENVIRONMENT", "").lower() == "production"
    price_id, billing_interval = resolve_essentials_price_id(tier_lower, request.interval)
    client_reference_id = checkout_client_reference_id(host)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=(
                f"{os.environ.get('FRONTEND_URL', '').rstrip('/')}/dashboard?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
                if (IS_PRODUCTION and os.environ.get('FRONTEND_URL', '').startswith("https://"))
                else "https://hosteva.onrender.com/dashboard?payment=success&session_id={CHECKOUT_SESSION_ID}"
                if IS_PRODUCTION
                else f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000').rstrip('/')}/success?session_id={{CHECKOUT_SESSION_ID}}"
            ),
            cancel_url=(
                f"{os.environ.get('FRONTEND_URL', '').rstrip('/')}/dashboard?payment=cancelled"
                if (IS_PRODUCTION and os.environ.get('FRONTEND_URL', '').startswith("https://"))
                else "https://hosteva.onrender.com/dashboard?payment=cancelled"
                if IS_PRODUCTION
                else f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000').rstrip('/')}/cancel"
            ),
            client_reference_id=client_reference_id,
            custom_text=essentials_checkout_custom_text(),
            metadata={
                "type": "subscription",
                "tier": "ESSENTIALS",
                "host_id": client_reference_id,
                "interval": billing_interval,
            },
        )
        return {
            "status": "pending",
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "client_reference_id": client_reference_id,
            "message": "Transaction initiated.",
        }
    except HTTPException:
        raise
    except Exception as e:
        if IS_PRODUCTION:
            raise HTTPException(
                status_code=502,
                detail="Payment provider unavailable. Please try again shortly.",
            )
        # Dev/test only
        return {
            "status": "pending",
            "checkout_url": f"/checkout-mock?session_id=session_12345&type=subscription&tier=ESSENTIALS&client_ref={client_reference_id}",
            "session_id": "session_12345",
            "client_reference_id": client_reference_id,
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
    
    IS_PRODUCTION = os.environ.get("ENVIRONMENT", "").lower() == "production"
    if IS_PRODUCTION and not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing signature")
        
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        if IS_PRODUCTION:
            raise HTTPException(status_code=400, detail="Invalid webhook event")
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
