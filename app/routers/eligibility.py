from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(prefix="/api/eligibility", tags=["Eligibility"])

class SearchRequest(BaseModel):
    address: str

@router.post("/search")
def search_eligibility(request: SearchRequest):
    # Mocking Google Places Details & Jurisdictional Logic
    address = request.address.lower()
    
    # Mock database logic
    if "miami beach" in address:
        status = "Ineligible"
        reason = "Short-term rentals are strictly prohibited in this specific zoning district."
    elif "orlando" in address:
        status = "Eligible"
        reason = "Property requires Orange County Tourist Tax registration."
    else:
        status = "Eligible"
        reason = "Standard state licensing applies."
        
    return {
        "address": request.address,
        "jurisdiction": "Mocked Jurisdiction",
        "status": status,
        "reason": reason
    }
