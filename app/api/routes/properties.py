from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_serializer
from typing import List, Optional, Any
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
    await asyncio.sleep(0.1)
    
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Wrap DB aggregation query in asyncio.wait_for (5 seconds)
        data = await asyncio.wait_for(aggregate_properties(db, current_user.get("username")), timeout=5.0)
    except asyncio.TimeoutError:
        # DLQ Logging requirement
        logger.error(f"DLQ Log: Database aggregation query timed out for user {current_user.get('username')}.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="System Degraded: Database query timed out"
        )
        
    return data
