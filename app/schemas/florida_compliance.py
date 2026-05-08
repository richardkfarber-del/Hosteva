from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ComplianceIssue(BaseModel):
    rule: str
    status: str
    message: str
    reference: str

class FloridaComplianceRequest(BaseModel):
    county: str = Field(..., description="County name: 'Pasco' or 'Hillsborough'")
    property_id: Optional[str] = Field(None, description="Optional property identifier")
    has_permit: bool = Field(False, description="Has short-term rental permit/license")
    has_vacation_license: bool = Field(False, description="Has vacation rental license (Hillsborough)")
    has_state_registration: bool = Field(False, description="Has Florida DBPR registration")
    has_fire_safety: bool = Field(False, description="Fire safety equipment verified")
    num_guests: int = Field(0, description="Number of guests")
    num_bedrooms: int = Field(0, description="Number of bedrooms")
    parking_spaces: int = Field(0, description="Number of parking spaces")
    last_inspection_date: Optional[str] = Field(None, description="Last inspection date (ISO format)")

class FloridaComplianceResponse(BaseModel):
    county: str
    is_compliant: bool
    issues: List[ComplianceIssue]
    evaluated_at: str
    total_rules_checked: int
    rules_passed: int
    property_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "county": "Pasco",
                "is_compliant": True,
                "issues": [],
                "evaluated_at": "2026-04-11T12:00:00",
                "total_rules_checked": 5,
                "rules_passed": 5,
                "property_id": "prop_123"
            }
        }
