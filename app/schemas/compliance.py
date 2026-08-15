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
    zoning_status: Optional[str] = None
    hoa_status: Optional[str] = None
    tax_status: Optional[str] = None
    safety_status: Optional[str] = None
    is_logged_in: bool = True

from datetime import date
from typing import List

class MunicipalRuleResponse(BaseModel):
    municipality_name: str
    jurisdiction_type: str
    str_permitted_raw: Optional[str] = None
    is_allowed: bool
    requires_permit: bool
    permit_name: Optional[str] = None
    minimum_stay_requirement: Optional[str] = None
    stay_restriction_days: Optional[int] = None
    occupancy_limits: Optional[str] = None
    tax_rate: Optional[float] = None
    source_url: Optional[str] = None
    last_verified_date: Optional[date] = None

    class Config:
        from_attributes = True

class HOARuleResponse(BaseModel):
    hoa_name: str
    location: str
    str_permitted: str
    minimum_lease_stay: Optional[str] = None
    rules_available: bool
    official_website: Optional[str] = None
    last_confirmed_date: Optional[date] = None
    key_rules_notes: Optional[str] = None

    class Config:
        from_attributes = True

class AddressComplianceChecklist(BaseModel):
    task_name: str
    status: str
    is_compliant: bool

class AddressComplianceResponse(BaseModel):
    address: str
    is_compliant: bool
    is_under_review: bool = False
    municipal_code: Optional[MunicipalRuleResponse] = None
    hoa_rule: Optional[HOARuleResponse] = None
    checklist: List[AddressComplianceChecklist] = []