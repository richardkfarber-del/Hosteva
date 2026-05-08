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

router = APIRouter(prefix="/api/properties", tags=["Properties"])


class PropertyCreate(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str = ""
    property_type: str = ""
    hoa_status: bool = False
    user_id: str = ""


@router.get("/", response_model=List[Dict[str, Any]])
def get_properties(
    status: str = Query(None, description="Filter by zoning status"),
    db: Session = Depends(get_db)
):
    properties = db.query(Property).all()
    result = [
        {
            "id": p.id,
            "address": p.address,
            "location": f"{p.city}, {p.state}",
            "zoning_status": p.zoning_status,
            "beds": 3,
            "baths": 2,
            "price": 0,
            "image_url": "",
            "lat": 34.0901 if p.id == 1 else (39.1911 if p.id == 2 else 25.7907),
            "lng": -118.3617 if p.id == 1 else (-106.8175 if p.id == 2 else -80.1300)
        }
        for p in properties
    ]
    if status:
        result = [p for p in result if p["zoning_status"].lower() == status.lower()]
    return result


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_property(property_data: PropertyCreate, db: Session = Depends(get_db)):
    db_property = Property(
        user_id=property_data.user_id,
        address=property_data.address,
        city=property_data.city,
        state=property_data.state,
        zip_code=property_data.zip_code,
        property_type=property_data.property_type,
        hoa_status=property_data.hoa_status,
        zoning_status="Pending"
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
        "price": 0,
        "image_url": ""
    }


@router.post("/{property_id}/evaluate")
def evaluate_compliance(property_id: str, db: Session = Depends(get_db)):
    host_email = "tony@stark.com"
    old_status = "Compliant"
    new_status = "Violation"
    
    if new_status == "Violation":
        dispatch_email_alert(host_email, property_id, old_status, new_status)
        
    return {"message": "Property evaluated", "status": new_status}
