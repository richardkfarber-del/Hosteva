import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import stripe
from app.dependencies import get_current_user, current_active_user

router = APIRouter()

async def check_subscription(user: str = Depends(current_active_user)):
    try:
        subscription = stripe.Subscription.retrieve(
            user.stripe_subscription_id,
            api_key=os.environ.get("STRIPE_API_KEY", "")
        )
        if subscription.status != 'active':
            return False
        return True
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/host-dashboard")
async def host_dashboard(user: str = Depends(current_active_user), is_subscribed: bool = Depends(check_subscription)):
    if not is_subscribed:
        return RedirectResponse(url='/subscription-page')
    # Logic for the host dashboard route
