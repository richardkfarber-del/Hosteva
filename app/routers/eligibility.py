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
    municipal_code = None
    if city:
        municipal_code = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike(city),
            MunicipalCode.jurisdiction_type.ilike("City"),
            ((MunicipalCode.state.ilike(state_code)) | (MunicipalCode.state.is_(None))),
        ).first()

    if not municipal_code and county:
        clean_county = county.replace(" County", "").strip()
        municipal_code = db.query(MunicipalCode).filter(
            (MunicipalCode.municipality_name.ilike(county))
            | (MunicipalCode.municipality_name.ilike(clean_county)),
            MunicipalCode.jurisdiction_type.ilike("County"),
            ((MunicipalCode.state.ilike(state_code)) | (MunicipalCode.state.is_(None))),
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
            status = STATUS_UNDER_REVIEW if state_code.upper() == "FL" else STATUS_NOT_COVERED
            conditions = (
                "Under Review — no curated municipal rule row for this locality. "
                "Hosteva does not invent a traffic-light zoning result."
                if status == STATUS_UNDER_REVIEW
                else "Not Covered — Phase I Free Audit is Florida-first; this locality is outside curated coverage."
            )
            return {
                "address": formatted_address,
                "jurisdiction": jurisdiction,
                "status": status,
                "determination": status,
                "conditions": conditions,
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

        # Have a municipal row — still do not emit GREEN/YELLOW/RED.
        # Point callers at the compliance checklist API for sold Free Audit.
        if municipal.str_prohibited or not municipal.is_allowed:
            determination = STATUS_UNDER_REVIEW
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
