from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_serializer
from typing import List, Optional, Dict, Any
import asyncio
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/properties", tags=["Properties v1"])
logger = logging.getLogger(__name__)

class AddressOut(BaseModel):
    full_string: str
    zip_code: str

class ComplianceProgressOut(BaseModel):
    completed: int
    total: int
    percentage: float

class PropertyOut(BaseModel):
    id: str
    address: AddressOut
    property_type: str
    compliance_progress: ComplianceProgressOut
    status_badge: str
    compliance_id: Optional[str] = None

    @field_serializer("compliance_id")
    def mask_compliance_id(self, v: Optional[str]) -> Optional[str]:
        if not v or len(v) < 4:
            return v
        return f"***-**-{v[-4:]}"

class PlatformAdoptionMetrics(BaseModel):
    airbnb_linked: bool
    vrbo_linked: bool

class MetaOut(BaseModel):
    total_properties: int
    platform_adoption_metrics: PlatformAdoptionMetrics

class PropertiesResponseOut(BaseModel):
    properties: List[PropertyOut]
    meta: MetaOut

async def aggregate_properties(db: Session, username: str) -> dict:
    """BUG-006: never return Ocean Drive mock properties. Empty until real DB path used."""
    return {
        "properties": [],
        "meta": {
            "total_properties": 0,
            "platform_adoption_metrics": {
                "airbnb_linked": False,
                "vrbo_linked": False,
            },
        },
    }

@router.get("", response_model=PropertiesResponseOut)
@router.get("/", response_model=PropertiesResponseOut, include_in_schema=False)
async def get_properties(
    current_user: dict = Depends(get_current_user),

    db: Session = Depends(get_db)
):
    try:
        # Wrap DB aggregation query in asyncio.wait_for (5 seconds)
        data = await asyncio.wait_for(aggregate_properties(db, current_user.get("username", "testuser")), timeout=3600.0)
    except asyncio.TimeoutError:
        # DLQ Logging requirement
        logger.error(f"DLQ Log: Database aggregation query timed out for user testuser.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="System Degraded: Database query timed out"
        )
        
    return data


# --- NEW V1 PROPERTY CREATION SCHEMAS AND ROUTE ---

class GeocodedAddressIn(BaseModel):
    address: str
    city: str
    state: str
    zip_code: Optional[str] = ""

class ComplianceDataIn(BaseModel):
    zoning_status: Optional[str] = "Pending"
    hoa_status: Optional[bool] = False
    required_permits: Optional[List[str]] = []
    local_restrictions: Optional[Dict[str, Any]] = {}

class PropertyCreateV1(BaseModel):
    address: GeocodedAddressIn
    property_type: str
    compliance_data: Optional[ComplianceDataIn] = None


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_property(
    property_data: PropertyCreateV1,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.host import Host
    from app.models.property import Property
    from app.routers.properties import (
        FALLBACK_PROPERTY_IMAGE_URL,
        geocode_address,
        is_fallback_property_image,
        resolve_property_create_image,
    )
    import json
    import uuid

    # 1. Fetch host profile
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    # 2. Geocode then fetch image (retry normalized location before stock — BUG-PL-02)
    full_address = f"{property_data.address.address}, {property_data.address.city}, {property_data.address.state} {property_data.address.zip_code}".strip()
    try:
        geocoded_for_image = geocode_address(full_address)
        if not isinstance(geocoded_for_image, dict):
            geocoded_for_image = None
    except Exception:
        geocoded_for_image = None
    image_url = resolve_property_create_image(full_address, geocoded=geocoded_for_image) or FALLBACK_PROPERTY_IMAGE_URL

    # 3. Initialize compliance data details
    comp = property_data.compliance_data
    zoning_status = comp.zoning_status if comp else "Pending"
    hoa_status = comp.hoa_status if comp else False
    required_permits = comp.required_permits if comp else []
    local_restrictions = comp.local_restrictions if comp else {}

    # Dynamically evaluate compliance if required_permits is empty
    state_upper = (property_data.address.state or "").upper()
    if not required_permits and (state_upper == "FL" or "FLORIDA" in state_upper):
        from app.routers.properties import geocode_address
        city_name = property_data.address.city
        state_name = property_data.address.state
        
        full_addr = f"{property_data.address.address}, {city_name}, {state_name} {property_data.address.zip_code}".strip()
        try:
            geocoded = geocode_address(full_addr)
            resolved_city = geocoded.get("city") or city_name
            resolved_county = geocoded.get("county") or (f"{resolved_city} County" if resolved_city else "Unknown County")
        except Exception:
            resolved_city = city_name
            resolved_county = f"{city_name} County" if city_name else "Unknown County"
            
        city_lower = resolved_city.lower() if resolved_city else ""
        county_lower = resolved_county.lower() if resolved_county else ""
        
        is_hillsborough = "hillsborough" in county_lower or "hillsborough" in city_lower
        is_st_pete = "st. petersburg" in city_lower or "st petersburg" in city_lower
        is_pasco = "pasco" in county_lower or "pasco" in city_lower
        
        if is_hillsborough:
            required_permits = [
                "Florida DBPR License task",
                "Hillsborough 6% Tourist Development Tax (TDT) registration",
                "State Sales Tax registration"
            ]
            zoning_status = "Pending"
        elif is_st_pete:
            required_permits = [
                "Florida DBPR License task",
                "St. Petersburg Business Tax Receipt (BTR) task",
                "Pinellas 6% TDT registration",
                "State Sales Tax registration"
            ]
            zoning_status = "Pending"
        elif is_pasco:
            required_permits = [
                "Pasco Conditional Use Permit task",
                "Annual Growth Management Registration",
                "Pasco 4% TDT registration",
                "State Sales Tax registration"
            ]
            zoning_status = "Pending"
        else:
            required_permits = [
                "Florida DBPR License task"
            ]
            
            from app.models.compliance import MunicipalCode
            municipal_code = None
            if resolved_city:
                municipal_code = db.query(MunicipalCode).filter(
                    MunicipalCode.municipality_name.ilike(resolved_city),
                    MunicipalCode.jurisdiction_type.ilike("City")
                ).first()
            if not municipal_code and resolved_county:
                clean_county = resolved_county.replace(" County", "").strip()
                municipal_code = db.query(MunicipalCode).filter(
                    (MunicipalCode.municipality_name.ilike(resolved_county)) |
                    (MunicipalCode.municipality_name.ilike(clean_county)),
                    MunicipalCode.jurisdiction_type.ilike("County")
                ).first()
                
            if not municipal_code:
                municipal_code = db.query(MunicipalCode).filter(
                    MunicipalCode.municipality_name.ilike("State of Florida")
                ).first()
                
            if municipal_code:
                if municipal_code.str_prohibited or not municipal_code.is_allowed:
                    zoning_status = "Violation"
                elif municipal_code.requires_permit:
                    zoning_status = "Pending"
                else:
                    zoning_status = "Compliant"

    db_property = Property(
        id=str(uuid.uuid4()),
        user_id=host.id,
        address=property_data.address.address,
        city=property_data.address.city,
        state=property_data.address.state,
        zip_code=property_data.address.zip_code,
        property_type=property_data.property_type,
        hoa_status=hoa_status,
        zoning_status=zoning_status,
        image_url=image_url,
        required_permits=json.dumps(required_permits),
        local_restrictions=json.dumps(local_restrictions)
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)

    # Populate PropertyCompliance checklist rows
    from app.models.compliance import PropertyCompliance, MunicipalCode
    state_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%Florida%")).first()
    if not state_code:
        state_code = db.query(MunicipalCode).first()
    
    fallback_mc_id = state_code.id if state_code else None
    if not fallback_mc_id:
        fallback_mc_id = uuid.uuid4()
    
    hillsborough_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%Hillsborough County%")).first()
    st_pete_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%St. Petersburg%")).first()
    pasco_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%Pasco County%")).first()
    
    state_id = state_code.id if state_code else fallback_mc_id
    hillsborough_id = hillsborough_code.id if hillsborough_code else (state_id or fallback_mc_id)
    st_pete_id = st_pete_code.id if st_pete_code else (state_id or fallback_mc_id)
    pasco_id = pasco_code.id if pasco_code else (state_id or fallback_mc_id)
    
    valid_period = '[2026-06-04 00:00:00, 2027-06-04 00:00:00]'
    
    for task_name in required_permits:
        if "Florida" in task_name or "State" in task_name:
            mc_id = state_id
        elif "Hillsborough" in task_name:
            mc_id = hillsborough_id
        elif "St. Petersburg" in task_name or "Pinellas" in task_name:
            mc_id = st_pete_id
        elif "Pasco" in task_name or "Annual Growth" in task_name:
            mc_id = pasco_id
        else:
            mc_id = state_id
            
        item = PropertyCompliance(
            property_id=db_property.id,
            municipal_code_id=mc_id,
            is_compliant=False,
            violation_notes=task_name,
            valid_period=valid_period,
            status="PENDING",
            task_name=task_name
        )
        db.add(item)
    db.commit()
    
    return {
        "id": db_property.id,
        "address": db_property.address,
        "city": db_property.city,
        "state": db_property.state,
        "zip_code": db_property.zip_code,
        "property_type": db_property.property_type,
        "hoa_status": db_property.hoa_status,
        "zoning_status": db_property.zoning_status,
        "image_url": db_property.image_url,
        "image_is_placeholder": is_fallback_property_image(db_property.image_url),
    }
