from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.florida_compliance import (
    FloridaComplianceRequest,
    FloridaComplianceResponse
)
from app.services.florida_compliance_engine import FloridaComplianceEngine

router = APIRouter(
    prefix="/api/florida-compliance",
    tags=["Florida Compliance Engine"]
)

@router.post("/evaluate", response_model=FloridaComplianceResponse)
def evaluate_florida_compliance(
    request: FloridaComplianceRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate property compliance against Florida municipal codes for Pasco or Hillsborough counties.
    
    This endpoint implements FEAT-003: Compliance Engine Base Implementation.
    """
    # Convert request to property details dictionary
    property_details = {
        "has_permit": request.has_permit,
        "has_vacation_license": request.has_vacation_license,
        "has_state_registration": request.has_state_registration,
        "has_fire_safety": request.has_fire_safety,
        "num_guests": request.num_guests,
        "num_bedrooms": request.num_bedrooms,
        "parking_spaces": request.parking_spaces,
        "last_inspection_date": request.last_inspection_date
    }
    
    # Evaluate compliance using the Florida Compliance Engine
    result = FloridaComplianceEngine.evaluate_compliance(
        county=request.county,
        property_details=property_details
    )
    
    # Add property_id to result if provided
    if request.property_id:
        result["property_id"] = request.property_id
    
    return result

@router.get("/counties")
def get_supported_counties():
    """
    Get list of supported Florida counties and their compliance requirements.
    """
    return {
        "supported_counties": ["Pasco", "Hillsborough"],
        "pasco_requirements": FloridaComplianceEngine.PASCO_CODES,
        "hillsborough_requirements": FloridaComplianceEngine.HILLSBOROUGH_CODES
    }

@router.get("/counties/{county}/requirements")
def get_county_requirements(county: str):
    """
    Get detailed compliance requirements for a specific county.
    """
    county_lower = county.lower()
    
    if county_lower == "pasco":
        return {
            "county": "Pasco",
            "requirements": FloridaComplianceEngine.PASCO_CODES
        }
    elif county_lower == "hillsborough":
        return {
            "county": "Hillsborough",
            "requirements": FloridaComplianceEngine.HILLSBOROUGH_CODES
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"County '{county}' not supported. Supported counties: Pasco, Hillsborough"
        )
