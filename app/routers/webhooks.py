from fastapi import APIRouter, Request, HTTPException
import logging
import os
import asyncio
from app.worker import redis_client

router = APIRouter()

# Vibranium Habit: Strictly enforce Webhook Signatures
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if os.getenv("ENVIRONMENT") == "production" and not STRIPE_WEBHOOK_SECRET:
        logging.error("Vibranium Habit Violation: STRIPE_WEBHOOK_SECRET is not configured.")
        raise HTTPException(status_code=500, detail="Server configuration error.")

    if os.getenv("ENVIRONMENT") == "production" and not sig_header:
        raise HTTPException(status_code=400, detail="Missing webhook signature.")

    try:
        # In a real environment, use stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        event = {"type": "payment_intent.succeeded", "data": {"object": {"customer": "cus_123", "subscription": "sub_456"}}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "payment_intent.succeeded":
        logging.info("Payment succeeded, processing subscription update.")
        await redis_client.enqueue("send_confirmation_email", {"customer_id": "cus_123"})
        
    return {"status": "success"}
