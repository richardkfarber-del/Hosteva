from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class PermitApplicationRequest(BaseModel):
    property_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "property_id": "prop_123"
            }
        }


class PermitApplicationResponse(BaseModel):
    application_id: str
    property_id: str
    county: str
    application_type: str
    status: str
    generated_at: datetime
    required_documents: List[str]
    compliance_summary: Dict[str, Any]
    estimated_processing_time: str
    next_steps: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "APP-2026-001234",
                "property_id": "prop_123",
                "county": "Pasco",
                "application_type": "Short-Term Rental Permit",
                "status": "draft",
                "generated_at": "2026-04-11T10:30:00",
                "required_documents": [
                    "Form HR-7020",
                    "Proof of Insurance",
                    "Fire Safety Inspection Certificate"
                ],
                "compliance_summary": {
                    "is_compliant": True,
                    "issues": []
                },
                "estimated_processing_time": "14-21 business days",
                "next_steps": [
                    "Review generated application",
                    "Upload required documents",
                    "Submit to county office"
                ]
            }
        }
