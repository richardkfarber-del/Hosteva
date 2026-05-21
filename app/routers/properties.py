from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from pydantic import BaseModel
from app.database import get_db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.email_service import dispatch_email_alert
from app.models.property import Property
from app.models.host import Host
from app.core.security import get_current_user

router = APIRouter(prefix="/api/properties", tags=["Properties"])


class PropertyCreate(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str = ""
    property_type: str = ""
    hoa_status: bool = False


@router.get("/", response_model=List[Dict[str, Any]])
def get_properties(
    status: str = Query(None, description="Filter by zoning status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    properties = db.query(Property).filter(Property.user_id == host.id).all()
    result = [
        {
            "id": p.id,
            "address": p.address,
            "location": f"{p.city}, {p.state}",
            "zoning_status": p.zoning_status,
            "beds": 3,
            "baths": 2,
            "price": 149 if p.property_type.lower() == "condo" else 249,
            "image_url": "",
            "lat": 34.0901,
            "lng": -118.3617
        }
        for p in properties
    ]
    if status:
        result = [p for p in result if p["zoning_status"].lower() == status.lower()]
    return result


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    db_property = Property(
        user_id=host.id,
        address=property_data.address,
        city=property_data.city,
        state=property_data.state,
        zip_code=property_data.zip_code,
        property_type=property_data.property_type,
        hoa_status=property_data.hoa_status,
        zoning_status="Compliant"  # default to Compliant for demo purposes
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return {
        "id": db_property.id,
        "address": db_property.address,
        "location": f"{db_property.city}, {db_property.state}",
        "zoning_status": db_property.zoning_status,
        "beds": 3,
        "baths": 2,
        "price": 249,
        "image_url": ""
    }


@router.post("/{property_id}/evaluate")
def evaluate_compliance(
    property_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    property_item = db.query(Property).filter(Property.id == property_id, Property.user_id == host.id).first()
    if not property_item:
        raise HTTPException(status_code=404, detail="Property not found")
        
    old_status = property_item.zoning_status
    new_status = "Compliant"
    
    # Simple logic
    property_item.zoning_status = new_status
    db.commit()
    
    if new_status == "Violation":
        dispatch_email_alert(host.email, property_id, old_status, new_status)
        
    return {"message": "Property evaluated", "status": new_status}
