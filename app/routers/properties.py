from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from app.database import get_db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.email_service import dispatch_email_alert

router = APIRouter(prefix="/api/properties", tags=["Properties"])

@router.get("/", response_model=List[Dict[str, Any]])
def get_properties(db: Session = Depends(get_db)):
    # Mocking properties list matching Shuri's dashboard requirement
    properties = [
        {
            "id": "1",
            "address": "123 Stark Tower Ave",
            "city": "New York",
            "zoning_district": "C-2",
            "compliance_status": "Compliant"
        },
        {
            "id": "2",
            "address": "456 Avengers Compound",
            "city": "Upstate",
            "zoning_district": "R-1",
            "compliance_status": "Violation"
        }
    ]
    return properties

@router.post("/{property_id}/evaluate")
def evaluate_compliance(property_id: str, db: Session = Depends(get_db)):
    # Mock status change trigger
    host_email = "tony@stark.com"
    old_status = "Compliant"
    new_status = "Violation"
    
    if new_status == "Violation":
        dispatch_email_alert(host_email, property_id, old_status, new_status)
        
    return {"message": "Property evaluated", "status": new_status}
