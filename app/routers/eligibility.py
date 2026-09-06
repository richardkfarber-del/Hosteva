import os
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
import requests
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.compliance import MunicipalCode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/eligibility", tags=["Eligibility"])

# Sold Free Audit outcomes (SYSTEM_DESIGN §5.1). Never GREEN/YELLOW/RED hash lights.
STATUS_UNDER_REVIEW = "UNDER_REVIEW"
STATUS_NOT_COVERED = "NOT_COVERED"
STATUS_ERROR = "ERROR"
STATUS_ALLOWED_WITH_CHECKLIST = "ALLOWED_WITH_CHECKLIST"


class SearchRequest(BaseModel):
    address: str


class EligibilityRequest(BaseModel):
    address: str
    place_id: Optional[str] = None


@router.get("/autocomplete")
def autocomplete_address(input: str, sessiontoken: str = None):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("Maps_API_KEY")

    if not api_key:
        return {"predictions": [], "error": "API key not configured"}

    try:
        autocomplete_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            "input": input,
            "key": api_key,
            "types": "address",
            "components": "country:us",
        }
        if sessiontoken:
            params["sessiontoken"] = sessiontoken

        response = requests.get(autocomplete_url, params=params, timeout=30)
        data = response.json()

        if data.get("status") != "OK":
            return {"predictions": [], "error": data.get("error_message", "Unknown error")}

        predictions = []
        for pred in data.get("predictions", []):
            predictions.append({
                "place_id": pred.get("place_id"),
                "description": pred.get("description"),
                "main_text": pred.get("structured_formatting", {}).get("main_text", ""),
                "secondary_text": pred.get("structured_formatting", {}).get("secondary_text", ""),
            })

        return {"predictions": predictions}

    except requests.exceptions.Timeout:
        logger.warning(f"Autocomplete request timed out for input: {input}")
        return {"predictions": [], "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Autocomplete request failed for input: {input}", exc_info=True)
        return {"predictions": [], "error": str(e)}


def _lookup_municipal(db: Session, city: str, county: str, state_code: str):
    """Align with compliance municipal aliasing (City of X / contains city)."""
    municipal_code = None
    state_ok = ((MunicipalCode.state.ilike(state_code)) | (MunicipalCode.state.is_(None)))

    if city:
        municipal_code = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike(city),
            MunicipalCode.jurisdiction_type.ilike("City"),
            state_ok,
        ).first()

        # Packs may store "City of Miami Beach" while geocode returns "Miami Beach"
        if not municipal_code:
            municipal_code = db.query(MunicipalCode).filter(
                MunicipalCode.municipality_name.ilike(f"City of {city}"),
                MunicipalCode.jurisdiction_type.ilike("City"),
                state_ok,
            ).first()

        if not municipal_code:
            municipal_code = db.query(MunicipalCode).filter(
                MunicipalCode.municipality_name.ilike(f"%{city}%"),
                MunicipalCode.jurisdiction_type.ilike("City"),
                state_ok,
            ).first()

        # Name matches City of X (or contains city) without requiring jurisdiction_type=City
        if not municipal_code:
            municipal_code = db.query(MunicipalCode).filter(
                (MunicipalCode.municipality_name.ilike(f"City of {city}"))
                | (MunicipalCode.municipality_name.ilike(f"%City of%{city}%")),
                state_ok,
            ).first()

    if not municipal_code and county:
        clean_county = county.replace(" County", "").strip()
        municipal_code = db.query(MunicipalCode).filter(
            (MunicipalCode.municipality_name.ilike(county))
            | (MunicipalCode.municipality_name.ilike(clean_county)),
            MunicipalCode.jurisdiction_type.ilike("County"),
            state_ok,
        ).first()

    return municipal_code


@router.post("/check")
def check_eligibility(request: EligibilityRequest, db: Session = Depends(get_db)):
    """
    Fail-closed eligibility for legacy callers.
    Never returns GREEN/YELLOW/RED from a hash lottery.
    Prefer GET /api/v1/compliance?address= for the sold Free Audit UI.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("Maps_API_KEY")

    if not api_key:
        return {
            "address": request.address,
            "jurisdiction": "Unknown",
            "status": STATUS_UNDER_REVIEW,
            "determination": STATUS_UNDER_REVIEW,
            "conditions": "Under Review — geocoding is not configured. This is not a zoning determination.",
            "traffic_light_removed": True,
        }

    try:
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": request.address, "key": api_key}
        response = requests.get(geocode_url, params=params, timeout=30)
        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            return {
                "address": request.address,
                "jurisdiction": "Unknown",
                "status": STATUS_UNDER_REVIEW,
                "determination": STATUS_UNDER_REVIEW,
                "conditions": "Under Review — address could not be geocoded. Not a zoning determination.",
                "traffic_light_removed": True,
            }

        result = data["results"][0]
        formatted_address = result.get("formatted_address", request.address)
        address_components = result.get("address_components", [])

        city = ""
        county = ""
        state = ""
        country = ""
        postal_code = ""

        for component in address_components:
            types = component.get("types", [])
            if "locality" in types:
                city = component.get("long_name", "")
            elif "administrative_area_level_2" in types:
                county = component.get("long_name", "")
            elif "administrative_area_level_1" in types:
                state = component.get("short_name", "")
            elif "country" in types:
                country = component.get("short_name", "")
            elif "postal_code" in types:
                postal_code = component.get("long_name", "")

        jurisdiction = f"{city}, {state}" if city and state else state or "Unknown"
        state_code = state.strip() if state else ""

        try:
            municipal = _lookup_municipal(db, city, county, state_code)
        except Exception:
            logger.exception("Municipal lookup failed; fail-closed to UNDER_REVIEW")
            return {
                "address": formatted_address,
                "jurisdiction": jurisdiction,
                "status": STATUS_UNDER_REVIEW,
                "determination": STATUS_UNDER_REVIEW,
                "conditions": "Under Review — rules database temporarily unavailable.",
                "components": {
                    "city": city,
                    "county": county,
                    "state": state,
                    "country": country,
                    "postal_code": postal_code,
                },
                "traffic_light_removed": True,
            }

        if not municipal:
            # SP-007: primary user-facing frame is Under Review (GO default) for both
            # FL miss and non-FL. status_reason distinguishes geography.
            is_fl = state_code.upper() == "FL"
            status = STATUS_UNDER_REVIEW
            status_reason = "MISSING_MUNICIPAL_CODE" if is_fl else "OUT_OF_PACK_GEOGRAPHY"
            conditions = (
                "Under Review — no curated municipal rule row for this locality. "
                "Hosteva does not invent a traffic-light zoning result."
                if is_fl
                else (
                    "Under Review — municipal Covered geography is Florida-only today. "
                    "This locality is outside the Florida municipal pack; we will not invent a result."
                )
            )
            try:
                from app.services.research_queue import enqueue_research
                enqueue_research(
                    db,
                    state=state_code.upper() or "ZZ",
                    municipality_name=city or (county.replace(" County", "").strip() if county else "unknown"),
                    jurisdiction_type="city" if city else "county",
                    sample_address=formatted_address,
                    trigger_reason=status_reason,
                )
            except Exception:
                pass
            return {
                "address": formatted_address,
                "jurisdiction": jurisdiction,
                "status": status,
                "determination": status,
                "conditions": conditions,
                "status_reason": status_reason,
                "coverage_tier": "UNDER_REVIEW",
                "components": {
                    "city": city,
                    "county": county,
                    "state": state,
                    "country": country,
                    "postal_code": postal_code,
                },
                "traffic_light_removed": True,
                "prefer_compliance_api": "/api/v1/compliance?address=",
            }

        # Have a municipal row — non-FL research seeds are still Under Review (Covered=FL only)
        mc_state = (municipal.state or state_code or "").upper()
        if state_code.upper() != "FL" or (mc_state and mc_state != "FL") or getattr(municipal, "is_ai_scraped", False):
            status = STATUS_UNDER_REVIEW
            conditions = (
                "Under Review — municipal Covered geography is Florida-only today "
                "(or this row is a non-authoritative research seed). Not legal advice."
            )
            try:
                from app.services.research_queue import enqueue_research
                enqueue_research(
                    db,
                    state=state_code.upper() or mc_state or "ZZ",
                    municipality_name=city or municipal.municipality_name,
                    jurisdiction_type="city",
                    sample_address=formatted_address,
                    trigger_reason="OUT_OF_PACK_GEOGRAPHY",
                )
            except Exception:
                pass
            return {
                "address": formatted_address,
                "jurisdiction": jurisdiction,
                "status": status,
                "determination": status,
                "conditions": conditions,
                "status_reason": "OUT_OF_PACK_GEOGRAPHY",
                "coverage_tier": "UNDER_REVIEW",
                "municipality_name": municipal.municipality_name,
                "components": {
                    "city": city,
                    "county": county,
                    "state": state,
                    "country": country,
                    "postal_code": postal_code,
                },
                "traffic_light_removed": True,
                "prefer_compliance_api": "/api/v1/compliance?address=",
            }

        # Have a curated FL municipal row — still do not emit GREEN/YELLOW/RED.
        # SP-007: Restricted FL pack is Covered ≠ Compliant; point at compliance API.
        if municipal.str_prohibited or not municipal.is_allowed:
            determination = "RESTRICTED"
            conditions = (
                f"Municipal rules for {municipal.municipality_name} indicate STR may be restricted or prohibited. "
                "Open Free Audit checklist via /api/v1/compliance for task details. Not legal advice."
            )
        else:
            determination = STATUS_ALLOWED_WITH_CHECKLIST
            conditions = (
                f"Curated municipal row found for {municipal.municipality_name}. "
                "Complete the Free Audit checklist — permits/taxes may still apply. Not legal advice."
            )

        return {
            "address": formatted_address,
            "jurisdiction": jurisdiction,
            "status": determination,
            "determination": determination,
            "conditions": conditions,
            "municipality_name": municipal.municipality_name,
            "components": {
                "city": city,
                "county": county,
                "state": state,
                "country": country,
                "postal_code": postal_code,
            },
            "traffic_light_removed": True,
            "prefer_compliance_api": "/api/v1/compliance?address=",
        }

    except requests.exceptions.Timeout:
        logger.warning(f"Eligibility check timed out for address: {request.address}")
        return {
            "address": request.address,
            "jurisdiction": "Unknown",
            "status": STATUS_UNDER_REVIEW,
            "determination": STATUS_UNDER_REVIEW,
            "conditions": "Under Review — geocoding timed out.",
            "traffic_light_removed": True,
        }
    except requests.exceptions.RequestException:
        logger.error(f"Eligibility check failed for address: {request.address}", exc_info=True)
        return {
            "address": request.address,
            "jurisdiction": "Unknown",
            "status": STATUS_ERROR,
            "determination": STATUS_ERROR,
            "conditions": "Error contacting geocoding service. Try again or use /api/v1/compliance.",
            "traffic_light_removed": True,
        }
