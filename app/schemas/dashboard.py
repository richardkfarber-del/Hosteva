from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AddressEligibilityStatus(BaseModel):
    """Address eligibility information for a property"""
    address: str
    city: str
    state: str
    jurisdiction: str
    status: str  # "Eligible", "Ineligible", "Pending Review"
    last_checked: Optional[datetime] = None
    issues: List[str] = []


class ListingHealthMetrics(BaseModel):
    """Health metrics for a property listing"""
    property_id: int
    property_name: str
    compliance_score: float  # 0-100
    zoning_status: str  # "Compliant", "Pending", "Violation"
    active_alerts: int
    last_inspection: Optional[datetime] = None
    violations: List[str] = []


class PropertyUnifiedView(BaseModel):
    """Unified view combining eligibility and health metrics"""
    property_id: int
    property_name: str
    location: str
    eligibility: AddressEligibilityStatus
    health: ListingHealthMetrics
    image_url: Optional[str] = None


class HostDashboardResponse(BaseModel):
    """Complete host dashboard data"""
    host_id: Optional[str] = None
    host_name: Optional[str] = None
    total_properties: int
    overall_compliance_score: float
    total_active_alerts: int
    properties: List[PropertyUnifiedView]
