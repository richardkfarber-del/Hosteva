"""US-018 / US-018c — Host-scoped duplicate address guard (dashboard add / API create).

Matching is per-host only: another host may save the same street address.

Normalize-before-match (US-018c / TE-011):
  1. Trim, case-fold, collapse whitespace on all parts.
  2. Canonicalize ZIP (digits only; soft when either side lacks ZIP; optional punctuation).
  3. Peel trailing city / state / ZIP from the address *line* when embedded
     (e.g. ``15758 Stable Run Drive, Spring Hill, FL 34610`` → street core
     ``15758 Stable Run Drive`` + locality Spring Hill / FL / 34610).
  4. Street cores must match; city/state soft when either side blank; ZIP soft
     when either side blank. Distinct streets that only share city/ZIP do NOT match.

Used by US-018 prevent and TE-010 cleanup (inherits automatically).
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

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

_STATE_ALIASES = {
    "florida": "fl",
    "fla": "fl",
}

# Common 2-letter US state tokens (casefold) for peeling trailing locality.
_US_STATE_ABBREVS = {
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id",
    "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
    "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok",
    "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv",
    "wi", "wy", "dc",
}

_ZIP_TOKEN_RE = re.compile(r"^(\d{5})(?:[-\s]?\d{4})?[,.]?$")
_TRAILING_STATE_ZIP_RE = re.compile(
    r"^(?P<head>.+?)[,\s]+(?P<state>[A-Za-z]{2}|Florida|Fla\.?)[,\s]+"
    r"(?P<zip>\d{5}(?:[-\s]?\d{4})?)[,.]?\s*$",
    re.IGNORECASE,
)
_TRAILING_CITY_STATE_ZIP_RE = re.compile(
    r"^(?P<head>.+?)[,\s]+(?P<city>[A-Za-z][A-Za-z .'-]*?)[,\s]+"
    r"(?P<state>[A-Za-z]{2}|Florida|Fla\.?)[,\s]+"
    r"(?P<zip>\d{5}(?:[-\s]?\d{4})?)[,.]?\s*$",
    re.IGNORECASE,
)
_TRAILING_ZIP_ONLY_RE = re.compile(
    r"^(?P<head>.+?)[,\s]+(?P<zip>\d{5}(?:[-\s]?\d{4})?)[,.]?\s*$",
)


def normalize_part(value: Optional[str]) -> str:
    """Trim, case-fold, collapse internal whitespace."""
    return " ".join((value or "").strip().casefold().split())


def normalize_state(value: Optional[str]) -> str:
    s = normalize_part(value)
    return _STATE_ALIASES.get(s, s)


def normalize_zip(value: Optional[str]) -> str:
    """Digits-only ZIP; keep 5-digit base (ignore +4 / punctuation)."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) >= 5:
        return digits[:5]
    return digits


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
        normalize_zip(zip_code) or normalize_part(zip_code),
    ]
    return " ".join(p for p in parts if p)


def _zip_compatible(a: str, b: str) -> bool:
    if not a or not b:
        return True
    return a == b


def _looks_like_zip(token: str) -> bool:
    return bool(_ZIP_TOKEN_RE.match((token or "").strip()))


def _looks_like_state(token: str) -> bool:
    s = normalize_state(token)
    return s in _US_STATE_ABBREVS or s in _STATE_ALIASES


def canonicalize_address_parts(
    address: Optional[str],
    city: Optional[str] = "",
    state: Optional[str] = "",
    zip_code: Optional[str] = "",
) -> Tuple[str, str, str, str]:
    """Normalize-before-match: street core + locality after peeling embedded tails.

    Returns ``(street_core, city, state, zip5)`` all casefolded/normalized.
    Street core is number+name only — trailing ``, City, ST ZIP`` is stripped
    from the address line when present; structured city/state/zip fill gaps.
    """
    raw = (address or "").strip()
    city_n = normalize_part(city)
    state_n = normalize_state(state)
    zip_n = normalize_zip(zip_code)

    street = raw
    peeled_city = ""
    peeled_state = ""
    peeled_zip = ""

    # Prefer full ", City, ST ZIP" peel
    m = _TRAILING_CITY_STATE_ZIP_RE.match(raw)
    if m:
        street = m.group("head").strip()
        peeled_city = normalize_part(m.group("city"))
        peeled_state = normalize_state(m.group("state"))
        peeled_zip = normalize_zip(m.group("zip"))
    else:
        m2 = _TRAILING_STATE_ZIP_RE.match(raw)
        if m2:
            street = m2.group("head").strip()
            peeled_state = normalize_state(m2.group("state"))
            peeled_zip = normalize_zip(m2.group("zip"))
            # If head still ends with ", City", peel that too when structured city empty
            if "," in street:
                left, right = street.rsplit(",", 1)
                right_n = normalize_part(right)
                if right_n and not _looks_like_zip(right_n) and not _looks_like_state(right_n):
                    street = left.strip()
                    peeled_city = right_n
        else:
            # Comma-split heuristic: last token ZIP, prior state, prior city
            if "," in raw:
                parts = [p.strip() for p in raw.split(",") if p.strip()]
                if len(parts) >= 2 and _looks_like_zip(parts[-1]):
                    peeled_zip = normalize_zip(parts[-1])
                    parts = parts[:-1]
                    if parts and _looks_like_state(parts[-1]):
                        peeled_state = normalize_state(parts[-1])
                        parts = parts[:-1]
                    elif parts:
                        # "FL 34610" already consumed as zip-only last; try "FL" in last remaining
                        last_bits = parts[-1].split()
                        if len(last_bits) >= 2 and _looks_like_state(last_bits[0]) and _looks_like_zip(
                            " ".join(last_bits[1:])
                        ):
                            peeled_state = normalize_state(last_bits[0])
                            peeled_zip = peeled_zip or normalize_zip(" ".join(last_bits[1:]))
                            parts = parts[:-1]
                    if len(parts) >= 2:
                        peeled_city = normalize_part(parts[-1])
                        street = ",".join(parts[:-1]).strip()
                    elif parts:
                        street = parts[0]
            else:
                m3 = _TRAILING_ZIP_ONLY_RE.match(raw)
                if m3 and not zip_n:
                    street = m3.group("head").strip()
                    peeled_zip = normalize_zip(m3.group("zip"))

    street_core = normalize_part(street)
    # Drop trailing punctuation left after peel
    street_core = street_core.rstrip(" ,.;")

    out_city = city_n or peeled_city
    out_state = state_n or peeled_state
    out_zip = zip_n or peeled_zip
    return street_core, out_city, out_state, out_zip


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
    """True when two address payloads are the same place under US-018 / US-018c rules."""
    a_street, a_city_n, a_state_n, a_zip_n = canonicalize_address_parts(
        a_address, a_city, a_state, a_zip
    )
    b_street, b_city_n, b_state_n, b_zip_n = canonicalize_address_parts(
        b_address, b_city, b_state, b_zip
    )
    if not a_street or not b_street:
        return False

    if a_street != b_street:
        # Fallback: full-line equality after classic normalize (preserves US-018 cases)
        a_full = full_line_key(a_address, a_city, a_state, a_zip)
        b_full = full_line_key(b_address, b_city, b_state, b_zip)
        return bool(a_full and b_full and a_full == b_full)

    state_ok = (not a_state_n or not b_state_n or a_state_n == b_state_n)
    city_ok = (not a_city_n or not b_city_n or a_city_n == b_city_n)
    if state_ok and city_ok and _zip_compatible(a_zip_n, b_zip_n):
        return True
    return False


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
