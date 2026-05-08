from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RegionBase(BaseModel):
    locality: str = Field(..., max_length=255)
    admin_area: str = Field(..., max_length=10)

class RegionCreate(RegionBase):
    pass

class RegionResponse(RegionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ZoningCodeBase(BaseModel):
    code_name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=1000)

class ZoningCodeCreate(ZoningCodeBase):
    region_id: str

class ZoningCodeResponse(ZoningCodeBase):
    id: str
    region_id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ComplianceRuleBase(BaseModel):
    eligibility_status: str = Field(..., pattern="^(GREEN|YELLOW|RED)$")
    is_str_allowed: bool
    requires_permit: bool = False
    min_stay_days: int = 1
    primary_residence_required: bool = False
    plain_english_conditions: Optional[str] = None
    permit_application_url: Optional[str] = None
    ordinance_reference_url: Optional[str] = None

class ComplianceRuleCreate(ComplianceRuleBase):
    zoning_id: str

class ComplianceRuleResponse(ComplianceRuleBase):
    id: str
    zoning_id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class EligibilityCheckRequest(BaseModel):
    address: str = Field(..., min_length=1)
    place_id: Optional[str] = None

class EligibilityCheckResponse(BaseModel):
    address: str
    status: str
    eligibility_status: str
    is_str_allowed: bool
    requires_permit: bool
    min_stay_days: int
    primary_residence_required: bool
    plain_english_conditions: Optional[str]
    permit_application_url: Optional[str]
    ordinance_reference_url: Optional[str]
    jurisdiction: Optional[str] = None
    zoning_code: Optional[str] = None