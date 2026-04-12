from fastapi import APIRouter, Request, HTTPException
import logging
import asyncio
from app.worker import redis_client

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = {"type": "payment_intent.succeeded", "data": {"object": {"customer": "cus_123", "subscription": "sub_456"}}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "payment_intent.succeeded":
        logging.info("Payment succeeded, processing subscription update.")
        await redis_client.enqueue("send_confirmation_email", {"customer_id": "cus_123"})
        
    return {"status": "success"}
