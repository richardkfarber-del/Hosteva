"""US-018 — Host-scoped duplicate address guard (dashboard add / API create).

Matching is per-host only: another host may save the same street address.
Normalize with trim + case-fold + collapsed whitespace; soft ZIP when either side lacks it.
Does not merge or clean existing duplicates (US-018b / TE-010).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.property import Property

# Wasp copy bank — docs/07_design/DUP_ADDRESS_ERROR_COPY.md §7
DUP_CODE = "DUPLICATE_ADDRESS"
DUP_BANNER_TITLE = "This address is already on your dashboard"
DUP_BANNER_BODY = (
    "We didn't add it again. Open the property you already saved to keep working from there."
)
DUP_ACTION_LABEL = "Open existing property"
DUP_SHORT_TOAST = "Already saved — open this property from your dashboard."
DUP_INLINE = "You already saved this address."
DUP_INLINE_HELPER = "Open it from your dashboard instead of adding it twice."
DUP_DISMISS = "Got it"


def normalize_part(value: Optional[str]) -> str:
    """Trim, case-fold, collapse internal whitespace."""
    return " ".join((value or "").strip().casefold().split())


def normalize_state(value: Optional[str]) -> str:
    s = normalize_part(value)
    if s in ("florida", "fla"):
        return "fl"
    return s


def full_line_key(
    address: Optional[str],
    city: Optional[str] = "",
    state: Optional[str] = "",
    zip_code: Optional[str] = "",
) -> str:
    parts = [
        normalize_part(address),
        normalize_part(city),
        normalize_state(state),
        normalize_part(zip_code),
    ]
    return " ".join(p for p in parts if p)


def _zip_compatible(a: str, b: str) -> bool:
    if not a or not b:
        return True
    return a == b


def addresses_equivalent(
    a_address: Optional[str],
    a_city: Optional[str],
    a_state: Optional[str],
    a_zip: Optional[str],
    b_address: Optional[str],
    b_city: Optional[str],
    b_state: Optional[str],
    b_zip: Optional[str],
) -> bool:
    """True when two address payloads are the same place under US-018 rules."""
    a_street = normalize_part(a_address)
    b_street = normalize_part(b_address)
    if not a_street or not b_street:
        return False

    a_city_n = normalize_part(a_city)
    b_city_n = normalize_part(b_city)
    a_state_n = normalize_state(a_state)
    b_state_n = normalize_state(b_state)
    a_zip_n = normalize_part(a_zip)
    b_zip_n = normalize_part(b_zip)

    if a_street == b_street:
        state_ok = (not a_state_n or not b_state_n or a_state_n == b_state_n)
        city_ok = (not a_city_n or not b_city_n or a_city_n == b_city_n)
        if state_ok and city_ok and _zip_compatible(a_zip_n, b_zip_n):
            return True

    a_full = full_line_key(a_address, a_city, a_state, a_zip)
    b_full = full_line_key(b_address, b_city, b_state, b_zip)
    return bool(a_full and b_full and a_full == b_full)


def find_host_duplicate_property(
    db: Session,
    host_id: str,
    address: Optional[str],
    city: Optional[str] = "",
    state: Optional[str] = "",
    zip_code: Optional[str] = "",
) -> Optional[Property]:
    """Return the existing property for this host that matches, or None."""
    if not host_id:
        return None
    props = db.query(Property).filter(Property.user_id == host_id).all()
    for prop in props:
        if addresses_equivalent(
            address,
            city,
            state,
            zip_code,
            prop.address,
            prop.city,
            prop.state,
            prop.zip_code or "",
        ):
            return prop
    return None


def duplicate_address_detail(prop: Property) -> Dict[str, Any]:
    """Structured FastAPI HTTPException detail for friendly UI (not bare 409 jargon)."""
    return {
        "code": DUP_CODE,
        "title": DUP_BANNER_TITLE,
        "message": DUP_BANNER_BODY,
        "inline": DUP_INLINE,
        "inline_helper": DUP_INLINE_HELPER,
        "action_label": DUP_ACTION_LABEL,
        "dismiss_label": DUP_DISMISS,
        "short_toast": DUP_SHORT_TOAST,
        "existing_property_id": prop.id,
        "existing_property_url": f"/manage/{prop.id}",
    }
