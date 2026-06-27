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
    # A mock database aggregation query taking time
    await asyncio.sleep(10.0)
    
    # Query could look like this: 
    # db.query(Property).filter(Property.user_id == username).all()
    # For now, returning mock data matching the UI contract from SPIKE-005
    
    return {
        "properties": [
            {
                "id": "prop_9a8b7c6d",
                "address": {
                    "full_string": "123 Ocean Drive, Unit 4B, Miami Beach, FL 33139",
                    "zip_code": "33139"
                },
                "property_type": "Condo",
                "compliance_progress": {
                    "completed": 4,
                    "total": 7,
                    "percentage": 57.1
                },
                "status_badge": "pending_compliance",
                "compliance_id": "123-45-6789"  # this will be masked by field_serializer
            }
        ],
        "meta": {
            "total_properties": 1,
            "platform_adoption_metrics": {
                "airbnb_linked": False,
                "vrbo_linked": False
            }
        }
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
    from app.routers.properties import fetch_real_property_image
    import json
    import uuid

    # 1. Fetch host profile
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    # 2. Fetch real property image or use placeholder
    full_address = f"{property_data.address.address}, {property_data.address.city}, {property_data.address.state} {property_data.address.zip_code}".strip()
    image_url = fetch_real_property_image(full_address)

    # 3. Initialize compliance data details
    comp = property_data.compliance_data
    zoning_status = comp.zoning_status if comp else "Pending"
    hoa_status = comp.hoa_status if comp else False
    required_permits = comp.required_permits if comp else []
    local_restrictions = comp.local_restrictions if comp else {}

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
    
    return {
        "id": db_property.id,
        "address": db_property.address,
        "city": db_property.city,
        "state": db_property.state,
        "zip_code": db_property.zip_code,
        "property_type": db_property.property_type,
        "hoa_status": db_property.hoa_status,
        "zoning_status": db_property.zoning_status,
        "image_url": db_property.image_url
    }
