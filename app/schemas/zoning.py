from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class LandUseTypeBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, pattern="^[a-zA-Z0-9_\-]+$")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class LandUseTypeResponse(LandUseTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ZoningDistrictBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, pattern="^[a-zA-Z0-9_\-]+$")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class ZoningDistrictResponse(ZoningDistrictBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ComplianceRuleTypeBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, pattern="^[a-zA-Z0-9_\-]+$")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    unit_of_measure: Optional[str] = Field(None, max_length=20)

class ComplianceRuleTypeResponse(ComplianceRuleTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ZoningRegulationBase(BaseModel):
    zoning_district_id: str = Field(..., max_length=100)
    land_use_type_id: str = Field(..., max_length=100)
    rule_type_id: str = Field(..., max_length=100)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    is_permitted: bool = False
    is_required: bool = False
    notes: Optional[str] = Field(None, max_length=1000)
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

class ZoningRegulationResponse(ZoningRegulationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ComplianceCheckRequest(BaseModel):
    property_id: str = Field(..., min_length=1, max_length=100, pattern="^[a-zA-Z0-9_\-]+$")
    zoning_district_id: str = Field(..., max_length=100)
    proposed_land_use_id: str = Field(..., max_length=100)
    actual_values: Dict[str, float] = Field(..., max_length=100) # Task 3: Payload size limits

class ComplianceReportResponse(BaseModel):
    id: str
    report_number: Optional[int] = None
    property_id: str
    zoning_district_id: str
    proposed_land_use_id: str
    is_compliant: bool
    issues: Optional[List[Dict[str, Any]]] = None
    analyst_notes: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True
