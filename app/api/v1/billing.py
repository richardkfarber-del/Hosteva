from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import stripe
import os
import json
import logging

from app.database import get_db
from app.core.security import get_current_user
from app.models.host import Host
from app.db_models import Subscription, PermitTransaction
from app.models.compliance import PropertyCompliance

# Configure stripe API keys
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
IS_PRODUCTION = os.getenv("ENVIRONMENT", "").lower() == "production"

if IS_PRODUCTION:
    if not stripe.api_key or str(stripe.api_key).startswith("sk_test"):
        raise RuntimeError("STRIPE_SECRET_KEY must be a live key in production")
    if not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET must be set in production")
FRONTEND_URL = os.getenv("FRONTEND_URL") or "http://localhost:3000"

router = APIRouter(
    prefix="/api/v1/billing",
    tags=["billing"]
)

class CheckoutRequest(BaseModel):
    tier: str  # "STARTER", "GROWTH", "ENTERPRISE", or "PERMIT_FILING"
    property_id: Optional[str] = None

@router.post("/checkout")
async def create_checkout_session(
    checkout_data: CheckoutRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Fetch host profile
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    client_reference_id = host.id if host else current_user.get("username", "user_mock_123")

    tier_val = checkout_data.tier.upper()

    # If it's a permit filing payment
    if tier_val == "PERMIT_FILING":
        if not checkout_data.property_id:
            raise HTTPException(status_code=400, detail="property_id is required for permit filing checkout")
        
        # Define mock or real price ID
        IS_PRODUCTION = os.getenv("ENVIRONMENT", "").lower() == "production"
        price_id = os.getenv("STRIPE_PRICE_PERMIT_FILING") or (
            "price_mock_permit_filing" if not IS_PRODUCTION else None
        )
        if not price_id:
            raise HTTPException(status_code=500, detail="Billing not configured")
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=FRONTEND_URL + '/dashboard?payment=success&session_id={CHECKOUT_SESSION_ID}',
                cancel_url=FRONTEND_URL + '/dashboard?payment=cancelled',
                client_reference_id=client_reference_id,
                metadata={
                    "type": "permit_filing",
                    "property_id": checkout_data.property_id
                }
            )
            # Create a pending permit transaction record
            new_tx = PermitTransaction(
                property_id=checkout_data.property_id,
                stripe_session_id=checkout_session.id,
                payment_status="PENDING",
                amount_paid=150.0
            )
            db.add(new_tx)
            db.commit()
            
            return {
                "status": "pending",
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id
            }
        except Exception as e:
            if IS_PRODUCTION:
                raise HTTPException(
                    status_code=502,
                    detail="Payment provider unavailable. Please try again shortly.",
                )
            # Fallback mock checkout URL for testing
            mock_session_id = f"cs_test_{client_reference_id[:8]}"
            new_tx = PermitTransaction(
                property_id=checkout_data.property_id,
                stripe_session_id=mock_session_id,
                payment_status="PENDING",
                amount_paid=150.0
            )
            db.add(new_tx)
            db.commit()
            return {
                "status": "pending",
                "checkout_url": f"/checkout-mock?session_id={mock_session_id}&type=permit_filing&property_id={checkout_data.property_id}",
                "session_id": mock_session_id,
                "warning": f"Mock fallback triggered: {e}"
            }
    
    # Otherwise it's a subscription checkout
    price_ids = {
        "FREE": os.getenv("STRIPE_PRICE_FREE") or ("price_mock_free" if not IS_PRODUCTION else None),
        "STARTER": os.getenv("STRIPE_PRICE_STARTER") or ("price_mock_starter" if not IS_PRODUCTION else None),
        "BASIC": os.getenv("STRIPE_PRICE_BASIC") or ("price_mock_starter" if not IS_PRODUCTION else None),
        "GROWTH": os.getenv("STRIPE_PRICE_GROWTH") or ("price_mock_growth" if not IS_PRODUCTION else None),
        "PRO": os.getenv("STRIPE_PRICE_PRO") or ("price_mock_growth" if not IS_PRODUCTION else None),
        "COMPLIANCE_ESSENTIALS": os.getenv("STRIPE_PRICE_COMPLIANCE_ESSENTIALS") or os.getenv("STRIPE_PRICE_BASIC") or ("price_mock_compliance_essentials" if not IS_PRODUCTION else None),
        "ENTERPRISE": os.getenv("STRIPE_PRICE_ENTERPRISE") or ("price_mock_enterprise" if not IS_PRODUCTION else None),
        "PREMIUM": os.getenv("STRIPE_PRICE_PREMIUM") or ("price_mock_enterprise" if not IS_PRODUCTION else None)
    }

    selected_price = price_ids.get(tier_val, price_ids["STARTER"])
    if IS_PRODUCTION and not selected_price:
        raise HTTPException(status_code=500, detail="Billing not configured")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': selected_price,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=FRONTEND_URL + '/dashboard?payment=success&session_id={CHECKOUT_SESSION_ID}',
            cancel_url=FRONTEND_URL + '/dashboard?payment=cancelled',
            client_reference_id=client_reference_id,
            metadata={
                "type": "subscription",
                "tier": tier_val
            }
        )
        return {
            "status": "pending",
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    except Exception as e:
        if IS_PRODUCTION:
            raise HTTPException(
                status_code=502,
                detail="Payment provider unavailable. Please try again shortly.",
            )
        mock_session_id = f"cs_test_sub_{client_reference_id[:8]}"
        return {
            "status": "pending",
            "checkout_url": f"/checkout-mock?session_id={mock_session_id}&type=subscription&tier={tier_val}",
            "session_id": mock_session_id,
            "warning": f"Mock fallback triggered: {e}"
        }

@router.post("/webhooks")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    payload = await request.body()
    
    # 1. Signature Verification with Local Fallback
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        # Fallback in local development
        if os.getenv("ENVIRONMENT") != "production":
            logging.warning(f"Stripe webhook signature validation failed locally: {e}. Parsing raw body.")
            try:
                event = json.loads(payload.decode("utf-8"))
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid JSON payload format.")
        else:
            raise HTTPException(status_code=400, detail=f"Signature verification failed: {e}")

    event_type = event.get("type")
    
    # 2. Event Handling Routing
    if event_type == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        client_ref = session.get("client_reference_id")
        stripe_cust = session.get("customer")
        stripe_sub = session.get("subscription")
        metadata = session.get("metadata") or {}
        session_id = session.get("id")
        mode = session.get("mode")

        # Route A: Subscription Fulfillments
        if mode == "subscription" or metadata.get("type") == "subscription":
            # Lookup host
            host = db.query(Host).filter(
                (Host.id == client_ref) | 
                (Host.username == client_ref) | 
                (Host.email == client_ref)
            ).first()
            if host:
                sub = db.query(Subscription).filter(Subscription.user_id == host.id).first()
                if not sub:
                    sub = Subscription(user_id=host.id)
                    db.add(sub)
                sub.stripe_customer_id = stripe_cust
                sub.stripe_subscription_id = stripe_sub
                sub.status = "active"
                sub.tier = metadata.get("tier") or "STARTER"
                sub.plan_details = stripe_sub or "activated"
                db.commit()
                logging.info(f"Stripe Webhook: Activated subscription {sub.tier} for host {host.id}")
        
        # Route B: Permit Filing Payments
        elif mode == "payment" or metadata.get("type") == "permit_filing":
            tx = db.query(PermitTransaction).filter(PermitTransaction.stripe_session_id == session_id).first()
            if tx:
                tx.payment_status = "PAID"
                if "amount_total" in session:
                    tx.amount_paid = float(session["amount_total"]) / 100.0
                
                # Auto-approve corresponding permit task in property compliance list
                comp_items = db.query(PropertyCompliance).filter(
                    PropertyCompliance.property_id == tx.property_id
                ).all()
                for item in comp_items:
                    # Fuzzy match item represent the permit/license filing
                    t_name = (item.task_name or "").lower()
                    v_notes = (item.violation_notes or "").lower()
                    if "permit" in t_name or "license" in t_name or "permit" in v_notes:
                        item.status = "APPROVED"
                        item.is_compliant = True
                db.commit()
                logging.info(f"Stripe Webhook: Paid permit transaction for property {tx.property_id}. Approved permit compliance tasks.")

    elif event_type in ["customer.subscription.updated", "customer.subscription.deleted"]:
        sub_obj = event.get("data", {}).get("object", {})
        sub_id = sub_obj.get("id")
        cust_id = sub_obj.get("customer")
        status_val = sub_obj.get("status")

        sub = db.query(Subscription).filter(
            (Subscription.stripe_subscription_id == sub_id) |
            (Subscription.stripe_customer_id == cust_id)
        ).first()
        
        if sub:
            if event_type == "customer.subscription.deleted" or status_val in ["canceled", "unpaid"]:
                sub.status = "inactive"
                sub.tier = "FREE"
            else:
                sub.status = status_val
            db.commit()
            logging.info(f"Stripe Webhook: Subscription {sub_id} status updated to {sub.status}")

    return {"status": "success"}
