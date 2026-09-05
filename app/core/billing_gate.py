"""Checkout kill-switch.

BILLING_ENABLED defaults OFF. Until auth-bound Stripe ships, no code path may
create Stripe Checkout Sessions unless this flag is explicitly true.
"""
from __future__ import annotations

import os

from fastapi import HTTPException


BILLING_UNAVAILABLE_DETAIL = "Billing temporarily unavailable"


def is_billing_enabled() -> bool:
    return os.getenv("BILLING_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")


def require_billing_enabled() -> None:
    """Hard-stop before any stripe.checkout.Session.create call."""
    if not is_billing_enabled():
        raise HTTPException(status_code=503, detail=BILLING_UNAVAILABLE_DETAIL)
