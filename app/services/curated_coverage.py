"""
Runtime Curated / Covered gate for Free Audit (compliance + eligibility).

Source of truth: docs/00_intake/CURATED_OPTION_B_GO.md (Richard GO 2026-09-06).
Gate: ONLY FL_CURATED_ALLOWLIST -> Covered checklist depth.
Other FL (Ocala, Gainesville, Jacksonville, Orange County, ...) -> UNDER_REVIEW.
Non-FL research seeds never elevate Covered.

Single maintainable frozenset -- expand for Option C later without changing gate logic.
Aliases: City of St. Petersburg, Sarasota City, Miami-Dade variants, PCB / Tampa Bay packs.
"""
from __future__ import annotations

import re
from typing import Any, Optional

# Full Option B (corridor + tourist+.gov + listed counties).
FL_CURATED_ALLOWLIST: frozenset[str] = frozenset(
    {
        # Corridor / pack-backed
        "kissimmee",
        "orlando",
        "panama city beach",
        "bay county",
        "bay",
        "miami beach",
        "city of miami beach",
        "miami-dade county",
        "miami-dade",
        "miami dade county",
        "miami dade",
        "tampa",
        "st. petersburg",
        "st petersburg",
        "city of st. petersburg",
        "city of st petersburg",
        "clearwater",
        "hillsborough county",
        "hillsborough",
        "pinellas county",
        "pinellas",
        "pasco county",
        "pasco",
        # Option B tourist cities
        "miami",
        "city of miami",
        "fort lauderdale",
        "hollywood",
        "key west",
        "destin",
        "naples",
        "sarasota",
        "sarasota city",
        "city of sarasota",
        "fort myers beach",
        "cape coral",
        "st. augustine",
        "st augustine",
        "saint augustine",
        "cocoa beach",
        "new smyrna beach",
        "fernandina beach",
        "marco island",
        "islamorada",
        "marathon",
        "anna maria",
        "st. pete beach",
        "st pete beach",
        "saint pete beach",
        "palm coast",
        "clermont",
        "boca raton",
        "doral",
        "sunny isles beach",
        "fort pierce",
        # Option B counties
        "broward county",
        "broward",
        "collier county",
        "collier",
        "monroe county",
        "monroe",
        "walton county",
        "walton",
        "st. johns county",
        "st johns county",
        "saint johns county",
        "st. johns",
        "st johns",
        "flagler county",
        "flagler",
        "gulf county",
        "gulf",
        "brevard county",
        "brevard",
    }
)

# Thin examples -- never Curated (Orange County Thin; Fort Myers city != Beach).
FL_CURATED_EXPLICIT_THIN: frozenset[str] = frozenset(
    {
        "orange county",
        "orange",
        "osceola county",
        "osceola",
        "ocala",
        "gainesville",
        "jacksonville",
        "pensacola",
        "fort myers",
        "city of fort myers",
        "panama city",
        "city of panama city",
    }
)


def normalize_municipality_name(name: Optional[str]) -> str:
    if not name:
        return ""
    n = name.strip().lower().replace("\u2019", "'")
    n = re.sub(r"\s+", " ", n)
    # "Sarasota City" -> "sarasota"; keep "panama city"
    if n.endswith(" city") and not n.startswith("panama "):
        bare = n[: -len(" city")].strip()
        if bare:
            n = bare
    return n


def is_name_on_curated_allowlist(municipality_name: Optional[str]) -> bool:
    key = normalize_municipality_name(municipality_name)
    if not key:
        return False
    if key in FL_CURATED_EXPLICIT_THIN:
        return False
    if key in FL_CURATED_ALLOWLIST:
        return True
    if key.startswith("city of "):
        bare = key[len("city of ") :].strip()
        if bare in FL_CURATED_EXPLICIT_THIN:
            return False
        bare_n = normalize_municipality_name(bare)
        if bare in FL_CURATED_ALLOWLIST or bare_n in FL_CURATED_ALLOWLIST:
            return True
    if key.endswith(" county"):
        bare = key[: -len(" county")].strip()
        if bare in FL_CURATED_EXPLICIT_THIN:
            return False
        if bare in FL_CURATED_ALLOWLIST or f"{bare} county" in FL_CURATED_ALLOWLIST:
            return True
    elif f"{key} county" in FL_CURATED_ALLOWLIST:
        return True
    return False


def is_curated_fl_municipal(
    municipal_code: Any,
    *,
    address_state: Optional[str] = None,
    geocoded_city: Optional[str] = None,
) -> bool:
    if not municipal_code:
        return False
    state_upper = (address_state or "").strip().upper()
    mc_state = (getattr(municipal_code, "state", None) or "FL").strip().upper()
    if state_upper and state_upper != "FL":
        return False
    if mc_state and mc_state != "FL":
        return False
    if getattr(municipal_code, "is_ai_scraped", False):
        return False
    name = getattr(municipal_code, "municipality_name", None) or ""
    if name.strip().lower() == "state of florida":
        return False
    return is_name_on_curated_allowlist(name)
