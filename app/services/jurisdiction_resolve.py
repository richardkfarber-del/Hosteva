"""
Municipal jurisdiction resolution for Free Audit / eligibility.

BUG-012: Spring Hill CDP mailing names often geocode as Hernando even when the
parcel/ZIP is Pasco (e.g. 15758 Stable Run Dr, ZIP 34610). Prefer curated county
truth over a non-curated city CDP match; apply known FL ZIP→county corrections.
Does NOT expand Hernando onto the Curated allowlist.
"""
from __future__ import annotations

import re
from typing import Any, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.compliance import MunicipalCode
from app.services.curated_coverage import is_name_on_curated_allowlist

# USPS ZCTA county truth for CDP/mailing edge cases where Google locality+county
# mis-route (Spring Hill mailing used in Pasco). Keep narrow — not a full ZIP DB.
FL_ZIP_COUNTY_OVERRIDES: dict[str, str] = {
    "34610": "Pasco County",  # Spring Hill / Shady Hills mailing — Pasco, not Hernando
}

_ZIP_RE = re.compile(r"\b(\d{5})(?:-\d{4})?\b")
# Prefer ZIP after state abbrev (avoids matching street number 15758 before 34610)
_ADDR_ZIP_RE = re.compile(
    r"(?:,\s*|\s+)(?:FL|Florida)\s+(\d{5})(?:-\d{4})?\b",
    re.IGNORECASE,
)


def extract_postal_code(
    *,
    address: Optional[str] = None,
    geocoded_postal: Optional[str] = None,
    address_components: Optional[list] = None,
) -> str:
    """Prefer geocode postal_code / components, else parse from address string."""
    if geocoded_postal:
        m = _ZIP_RE.search(str(geocoded_postal))
        if m:
            return m.group(1)
    if address_components:
        for c in address_components:
            types = c.get("types") or []
            if "postal_code" in types:
                long_name = (c.get("long_name") or "").strip()
                m = _ZIP_RE.search(long_name)
                if m:
                    return m.group(1)
    if address:
        m = _ADDR_ZIP_RE.search(address)
        if m:
            return m.group(1)
        # Fallback: last 5-digit token in the string (street # is usually first)
        matches = _ZIP_RE.findall(address)
        if matches:
            return matches[-1]
    return ""


def correct_geocode_components(
    *,
    city: Optional[str],
    county: Optional[str],
    state: Optional[str],
    postal_code: Optional[str] = None,
    address: Optional[str] = None,
    address_components: Optional[list] = None,
) -> Tuple[str, str, str, str]:
    """
    Return (city, county, state, postal_code) after ZIP→county corrections.
    Only overrides county when a known FL ZIP maps to a different county.
    """
    city_out = (city or "").strip()
    county_out = (county or "").strip()
    state_out = (state or "").strip()
    zip_out = extract_postal_code(
        address=address,
        geocoded_postal=postal_code,
        address_components=address_components,
    )

    state_upper = state_out.upper()
    if len(state_upper) > 2:
        state_map = {
            "florida": "FL",
            "california": "CA",
            "texas": "TX",
            "new york": "NY",
        }
        state_out = state_map.get(state_out.lower(), state_out)
        state_upper = state_out.upper()

    if zip_out and (state_upper == "FL" or not state_upper):
        override = FL_ZIP_COUNTY_OVERRIDES.get(zip_out)
        if override:
            county_out = override
            if not state_upper:
                state_out = "FL"

    return city_out, county_out, state_out, zip_out


def _state_filter(state_code: str):
    return (MunicipalCode.state.ilike(state_code)) | (MunicipalCode.state.is_(None))


def _lookup_city(db: Session, city: str, state_code: str) -> Optional[MunicipalCode]:
    if not city:
        return None
    state_ok = _state_filter(state_code)
    municipal_code = (
        db.query(MunicipalCode)
        .filter(
            MunicipalCode.municipality_name.ilike(city),
            MunicipalCode.jurisdiction_type.ilike("City"),
            state_ok,
        )
        .first()
    )
    if not municipal_code:
        municipal_code = (
            db.query(MunicipalCode)
            .filter(
                MunicipalCode.municipality_name.ilike(f"City of {city}"),
                MunicipalCode.jurisdiction_type.ilike("City"),
                state_ok,
            )
            .first()
        )
    if not municipal_code:
        municipal_code = (
            db.query(MunicipalCode)
            .filter(
                MunicipalCode.municipality_name.ilike(city),
                state_ok,
            )
            .first()
        )
    if not municipal_code:
        # Eligibility-style loose contains (City of X) without requiring type=City
        municipal_code = (
            db.query(MunicipalCode)
            .filter(
                (MunicipalCode.municipality_name.ilike(f"City of {city}"))
                | (MunicipalCode.municipality_name.ilike(f"%City of%{city}%")),
                state_ok,
            )
            .first()
        )
    if not municipal_code:
        municipal_code = (
            db.query(MunicipalCode)
            .filter(
                MunicipalCode.municipality_name.ilike(f"%{city}%"),
                MunicipalCode.jurisdiction_type.ilike("City"),
                state_ok,
            )
            .first()
        )
    return municipal_code


def _lookup_county(db: Session, county: str, state_code: str) -> Optional[MunicipalCode]:
    if not county:
        return None
    clean_county = county.replace(" County", "").strip()
    state_ok = _state_filter(state_code)
    return (
        db.query(MunicipalCode)
        .filter(
            (MunicipalCode.municipality_name.ilike(county))
            | (MunicipalCode.municipality_name.ilike(clean_county)),
            MunicipalCode.jurisdiction_type.ilike("County"),
            state_ok,
        )
        .first()
    )


def lookup_municipal_code(
    db: Session,
    *,
    city: Optional[str],
    county: Optional[str],
    state: Optional[str],
    postal_code: Optional[str] = None,
    address: Optional[str] = None,
    address_components: Optional[list] = None,
    allow_state_of_florida_fallback: bool = False,
) -> Tuple[Optional[MunicipalCode], str, str, str, str]:
    """
    Resolve MunicipalCode for geocoded locality.

    Preference:
    1. ZIP→county correction (Pasco 34610 vs Hernando Spring Hill CDP).
    2. City match when that municipality is on Curated allowlist.
    3. Else county match (Curated Pasco path for Stable Run).
    4. Else non-curated city match (Thin / Under Review path).
    5. Optional State of Florida fallback (compliance API only).

    Returns (municipal_code, city, county, state, postal_code).
    """
    city_c, county_c, state_c, zip_c = correct_geocode_components(
        city=city,
        county=county,
        state=state,
        postal_code=postal_code,
        address=address,
        address_components=address_components,
    )
    state_code = state_c.strip() if state_c else ""
    if len(state_code) > 2:
        # already normalized in correct_geocode_components for common names
        pass

    city_row = _lookup_city(db, city_c, state_code) if city_c else None
    county_row = _lookup_county(db, county_c, state_code) if county_c else None

    chosen: Optional[MunicipalCode] = None
    if city_row and is_name_on_curated_allowlist(city_row.municipality_name):
        chosen = city_row
    elif county_row and is_name_on_curated_allowlist(county_row.municipality_name):
        # Prefer curated county over non-curated CDP city (Spring Hill → Pasco)
        chosen = county_row
    elif city_row:
        chosen = city_row
    elif county_row:
        chosen = county_row

    if (
        not chosen
        and allow_state_of_florida_fallback
        and (state_code.upper() == "FL" or not state_code)
    ):
        chosen = (
            db.query(MunicipalCode)
            .filter(
                MunicipalCode.municipality_name.ilike("State of Florida"),
                (MunicipalCode.state.ilike("FL")) | (MunicipalCode.state.is_(None)),
            )
            .first()
        )

    return chosen, city_c, county_c, state_c, zip_c
