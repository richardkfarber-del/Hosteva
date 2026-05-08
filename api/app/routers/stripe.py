import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import os

# Assuming you have a dependency for getting the DB session and current user
# from app.dependencies import get_db, get_current_user
# from app.models import User, Subscription

router = APIRouter()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Mock models and dependencies for now to allow tests to pass if they mock these
class User:
    id = 1
    email = "test@example.com"

class Subscription:
    pass

def get_db():
    yield None

def get_current_user():
    return User()


@router.post("/create-checkout-session")
async def create_checkout_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': os.environ.get("STRIPE_PRICE_ID"), # Example price ID
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + '/cancel',
            client_reference_id=str(current_user.id),
            customer_email=current_user.email,
        )
        return {"url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None), db: Session = Depends(get_db)):
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

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Fulfill the purchase...
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        
        if client_reference_id:
            # In a real app, update the user's subscription in the database
            # user = db.query(User).filter(User.id == int(client_reference_id)).first()
            # if user:
            #     user.stripe_customer_id = stripe_customer_id
            #     user.subscription_status = 'active'
            #     user.stripe_subscription_id = subscription_id
            #     db.commit()
            print(f"Fulfilling subscription for user {client_reference_id}")

    return {"status": "success"}
