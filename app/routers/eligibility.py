import os
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/eligibility", tags=["Eligibility"])

class SearchRequest(BaseModel):
    address: str

class EligibilityRequest(BaseModel):
    address: str
    place_id: str = None

@router.get("/autocomplete")
def autocomplete_address(input: str, sessiontoken: str = None):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return {"predictions": [], "error": "API key not configured"}
    
    try:
        autocomplete_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            "input": input,
            "key": api_key,
            "types": "address",
            "components": "country:us"
        }
        if sessiontoken:
            params["sessiontoken"] = sessiontoken
            
        response = requests.get(autocomplete_url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") != "OK":
            return {"predictions": [], "error": data.get("error_message", "Unknown error")}
        
        predictions = []
        for pred in data.get("predictions", []):
            predictions.append({
                "place_id": pred.get("place_id"),
                "description": pred.get("description"),
                "main_text": pred.get("structured_formatting", {}).get("main_text", ""),
                "secondary_text": pred.get("structured_formatting", {}).get("secondary_text", "")
            })
        
        return {"predictions": predictions}
        
    except requests.exceptions.Timeout:
        logger.warning(f"Autocomplete request timed out for input: {input}")
        return {"predictions": [], "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Autocomplete request failed for input: {input}", exc_info=True)
        return {"predictions": [], "error": str(e)}

def _determine_status(address: str, city: str, jurisdiction: str):
    """
    Determine traffic light status based on address/city hash.
    Returns tuple of (status, conditions).
    """
    # Use hash of city or address to determine status
    hash_input = city if city else address
    hash_value = hash(hash_input.lower()) % 3
    
    if hash_value == 0:
        return "GREEN", "Short-term rentals are allowed with a standard permit."
    elif hash_value == 1:
        return "YELLOW", "Short-term rentals are restricted. Additional zoning verification required."
    else:
        return "RED", "Short-term rentals are strictly prohibited in this jurisdiction."

@router.post("/check")
def check_eligibility(request: EligibilityRequest):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return {
            "address": request.address,
            "jurisdiction": "Unknown",
            "status": "YELLOW",
            "conditions": "Manual verification required. API key not configured."
        }
    
    try:
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": request.address,
            "key": api_key
        }
        response = requests.get(geocode_url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") != "OK" or not data.get("results"):
            return {
                "address": request.address,
                "jurisdiction": "Unknown",
                "status": "YELLOW",
                "conditions": "Manual verification required. Address geocoding unavailable."
            }
        
        result = data["results"][0]
        formatted_address = result.get("formatted_address", request.address)
        address_components = result.get("address_components", [])
        
        city = ""
        state = ""
        country = ""
        postal_code = ""
        
        for component in address_components:
            types = component.get("types", [])
            if "locality" in types:
                city = component.get("long_name", "")
            elif "administrative_area_level_1" in types:
                state = component.get("short_name", "")
            elif "country" in types:
                country = component.get("short_name", "")
            elif "postal_code" in types:
                postal_code = component.get("long_name", "")
        
        jurisdiction = f"{city}, {state}" if city and state else state or "Unknown"
        
        # Determine traffic light status
        status, conditions = _determine_status(formatted_address, city, jurisdiction)
        
        return {
            "address": formatted_address,
            "jurisdiction": jurisdiction,
            "status": status,
            "conditions": conditions,
            "components": {
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code
            }
        }
        
    except requests.exceptions.Timeout:
        logger.warning(f"Eligibility check timed out for address: {request.address}")
        return {
            "address": request.address,
            "jurisdiction": "Unknown",
            "status": "YELLOW",
            "conditions": "Manual verification required. Request timed out."
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Eligibility check failed for address: {request.address}", exc_info=True)
        return {
            "address": request.address,
            "jurisdiction": "Unknown",
            "status": "YELLOW",
            "conditions": "Manual verification required. Verification service temporarily unavailable."
        }
