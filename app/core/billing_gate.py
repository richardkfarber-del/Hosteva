"""Checkout kill-switch + authenticated Host resolution for Stripe.

BILLING_ENABLED defaults OFF. Stripe Checkout Sessions are created only when
this flag is true AND the caller is an authenticated Host (never user_mock_123).
"""
from __future__ import annotations

import os
from typing import Optional, Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.host import Host


BILLING_UNAVAILABLE_DETAIL = "Billing temporarily unavailable"

# Phase I Compliance Essentials — Stripe Product / Checkout honesty (BUG-LAUNCH-01 / SP-002 Option A)
ESSENTIALS_PRODUCT_DESCRIPTION = (
    "Florida STR compliance research: municipal checklists, .gov links, and "
    "fee notes when available. Not legal advice."
)


def essentials_checkout_custom_text() -> dict:
    """Checkout Session custom_text so submit area shows Phase I copy even if Dashboard Product is stale."""
    return {"submit": {"message": ESSENTIALS_PRODUCT_DESCRIPTION}}

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


# --- Essentials entitlement (US-006) ---
# Active Essentials = Subscription.status == "active" AND tier in ESSENTIALS (+ aliases)

ESSENTIALS_TIER_ALIASES = frozenset({
    "essentials",
    "compliance_essentials",
    "complianceessentials",
    "starter",
    "basic",
    "pro",
    "growth",
    "premium",
    "enterprise",
})

ENTITLEMENT_REQUIRED_DETAIL = (
    "Essentials subscription required for full checklist depth. "
    "Please upgrade to Compliance Essentials."
)


def _tier_key(raw: Optional[str]) -> str:
    if not raw:
        return ""
    return (
        str(raw)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def is_essentials_tier(tier: Optional[str]) -> bool:
    """True if tier string maps to Phase I Essentials (incl. legacy aliases)."""
    key = _tier_key(tier)
    if not key or key in ("free", "inactive", "canceled", "cancelled"):
        return False
    if key in ESSENTIALS_TIER_ALIASES:
        return True
    if "essential" in key or "compliance" in key:
        return True
    return False


def normalize_essentials_tier(raw: Optional[str]) -> str:
    """Persist ESSENTIALS for any paid/alias activation; FREE otherwise."""
    key = _tier_key(raw)
    if not key or key in ("free", "inactive", "canceled", "cancelled"):
        return "FREE"
    if is_essentials_tier(raw):
        return "ESSENTIALS"
    # Phase I: unknown paid-ish labels still map to Essentials
    return "ESSENTIALS"


def subscription_is_active_essentials(sub: Any) -> bool:
    """Active Essentials entitlement from a Subscription row (or None)."""
    if sub is None:
        return False
    if getattr(sub, "status", None) != "active":
        return False
    tier = getattr(sub, "tier", None)
    plan = getattr(sub, "plan_details", None)
    return is_essentials_tier(tier) or is_essentials_tier(plan if isinstance(plan, str) else None)


def get_host_subscription(db: Session, host: Host):
    """Load Subscription for host via explicit query only.

    Never touch host.subscription relationship — lazy-load failures on Render
    were turning Free checklist/tasks into HTTP 500 instead of 403 (BUG_US006).
    """
    if host is None or db is None:
        return None
    from app.db_models import Subscription

    try:
        return db.query(Subscription).filter(Subscription.user_id == host.id).first()
    except Exception:
        # Fail closed as non-entitled rather than 500 the gate
        return None


def host_has_active_essentials(db: Session, host: Optional[Host]) -> bool:
    if host is None:
        return False
    try:
        return subscription_is_active_essentials(get_host_subscription(db, host))
    except Exception:
        return False


def require_active_essentials(db: Session, host: Optional[Host]) -> None:
    """Raise 403 if host lacks active Essentials entitlement. Never 500."""
    try:
        entitled = host_has_active_essentials(db, host)
    except Exception:
        entitled = False
    if not entitled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ENTITLEMENT_REQUIRED_DETAIL,
        )


def display_tier_label(sub: Any) -> str:
    """UI label for /users/me: Compliance Essentials | Free Tier."""
    if subscription_is_active_essentials(sub):
        return "Compliance Essentials"
    return "Free Tier"


def me_entitlement_fields(db: Session, host: Optional[Host]) -> dict:
    """Consistent entitlement fields for /users/me and /api/v1/users/me."""
    sub = get_host_subscription(db, host) if host else None
    active = subscription_is_active_essentials(sub)
    return {
        "tier": "Compliance Essentials" if active else "Free Tier",
        "has_active_subscription": active,
        "subscription_tier": (getattr(sub, "tier", None) or "FREE") if sub else "FREE",
        "subscription_status": (getattr(sub, "status", None) or "inactive") if sub else "inactive",
    }
