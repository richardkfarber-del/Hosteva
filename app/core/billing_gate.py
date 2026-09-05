"""Checkout kill-switch + authenticated Host resolution for Stripe.

BILLING_ENABLED defaults OFF. Stripe Checkout Sessions are created only when
this flag is true AND the caller is an authenticated Host (never user_mock_123).
"""
from __future__ import annotations

import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.host import Host


BILLING_UNAVAILABLE_DETAIL = "Billing temporarily unavailable"
FORBIDDEN_REFERENCE_IDS = frozenset({"user_mock_123", "mock", "anonymous", "guest"})

# Legacy / alias tiers → Essentials monthly
_MONTHLY_TIERS = frozenset({
    "essentials",
    "compliance_essentials",
    "starter",
    "basic",
    "pro",
    "growth",
    "free",
})
# Legacy tiers → Essentials yearly
_YEARLY_TIERS = frozenset({
    "premium",
    "enterprise",
})


def is_billing_enabled() -> bool:
    return os.getenv("BILLING_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")


def require_billing_enabled() -> None:
    """Hard-stop before any stripe.checkout.Session.create call."""
    if not is_billing_enabled():
        raise HTTPException(status_code=503, detail=BILLING_UNAVAILABLE_DETAIL)


def require_checkout_host(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Host:
    """JWT-required Host for checkout. Never returns a mock sentinel identity."""
    username = (current_user or {}).get("username")
    if not username or str(username).strip().lower() in FORBIDDEN_REFERENCE_IDS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for checkout",
            headers={"WWW-Authenticate": "Bearer"},
        )
    host = db.query(Host).filter(Host.username == username).first()
    if not host or not getattr(host, "id", None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for checkout",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if str(host.id).strip().lower() in FORBIDDEN_REFERENCE_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid checkout identity",
        )
    return host


def checkout_client_reference_id(host: Host) -> str:
    """Stripe client_reference_id must be the real Host UUID/string id."""
    ref = str(host.id)
    if ref.strip().lower() in FORBIDDEN_REFERENCE_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid checkout identity",
        )
    return ref


def resolve_essentials_price_id(tier: str, interval: Optional[str] = None) -> tuple[str, str]:
    """Map tier/interval to Phase I Essentials Stripe price id.

    Returns (price_id, billing_interval) where billing_interval is monthly|yearly.
    Env preference:
      monthly: STRIPE_PRICE_ESSENTIALS_MONTHLY → STRIPE_PRICE_COMPLIANCE_ESSENTIALS → STRIPE_PRICE_BASIC
      yearly:  STRIPE_PRICE_ESSENTIALS_YEARLY → STRIPE_PRICE_PREMIUM
    Legacy: starter/basic/pro → monthly; premium/enterprise → yearly.
    """
    is_production = os.environ.get("ENVIRONMENT", "").lower() == "production"
    tier_key = (tier or "").strip().lower()
    interval_key = (interval or "").strip().lower() if interval else ""

    if interval_key in ("yearly", "year", "annual", "annually"):
        use_yearly = True
    elif interval_key in ("monthly", "month"):
        use_yearly = False
    elif tier_key in _YEARLY_TIERS:
        use_yearly = True
    else:
        # essentials / compliance_essentials / starter / basic / pro / growth / default
        use_yearly = False

    if use_yearly:
        price_id = (
            os.environ.get("STRIPE_PRICE_ESSENTIALS_YEARLY")
            or os.environ.get("STRIPE_PRICE_PREMIUM")
            or ("price_mock_essentials_yearly" if not is_production else None)
        )
        billing_interval = "yearly"
    else:
        price_id = (
            os.environ.get("STRIPE_PRICE_ESSENTIALS_MONTHLY")
            or os.environ.get("STRIPE_PRICE_COMPLIANCE_ESSENTIALS")
            or os.environ.get("STRIPE_PRICE_BASIC")
            or ("price_mock_essentials_monthly" if not is_production else None)
        )
        billing_interval = "monthly"

    if not price_id:
        raise HTTPException(status_code=500, detail="Billing not configured")
    return price_id, billing_interval
