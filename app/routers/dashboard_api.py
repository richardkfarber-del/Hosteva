from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.schemas.dashboard import (
    HostDashboardResponse,
    PropertyUnifiedView,
    AddressEligibilityStatus,
    ListingHealthMetrics
)
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

MOCK_PROPERTIES = [
    {"id": 1, "name": "The Obsidian Sanctuary", "location": "West Hollywood, CA", "price": 1250, "beds": 4, "baths": 3.5, "zoning_status": "Compliant", "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDtDfxPMaRsQxdORVLEVnaJqJkfWn-BIXgFNQc-W5TalH7m8KmPsVxzaGJymts4o67euXEuPWg-baUXk4eMJfPEe5BNL4ewYRx5BGIISm6s-VSgn_4yYv07IC2nEmtgMELJXzcESUQg9C8Wd4ktY2bTxOBeFDG9fiGcZVp6tsDSSyt5Noy0pJAbcaZD7TEfNffu00ipN1I6qeoV-KfAp73nAnWN2l8WW7hV8bKR-DY9XH9gD1QXSQZzfO7x5soMp5tvDsIGbgRGAlw", "lat": 34.0901, "lng": -118.3617},
    {"id": 2, "name": "The Glass Pavilion", "location": "Aspen, CO", "price": 2400, "beds": 5, "baths": 6, "zoning_status": "Pending", "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuBq14jjRyvZzz5UTQ0eMg5f3Tb372I7mv8Yrv6TY6sV_E4IRmFPA9xkERl57KcoDkzf8ltJE710_mWm9ijIJBp9YOOLmP9XuxQmdaJfrn4sqja-Py71hfXYXCpHUpb3lceiSPUTdzYkw_0n2v2n-UO4PvSh56L6oRhsLSfL2X0SP-VMGsDLeIH8Sw1pjKpBSnQQoYGfk5_wZ7qxULyQFOyddN3I7xAgbjPRLZFhFVQNfulIKKZDNVG_Jy01u1swzQDGBbk_ANZ95HE", "lat": 39.1911, "lng": -106.8175},
    {"id": 3, "name": "Azure Loft Estate", "location": "Miami Beach, FL", "price": 850, "beds": 3, "baths": 3, "zoning_status": "Violation", "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDNvPJa8r3BvpFcxDHWTuHvngW3w2L31pdYX1LsjjO8rspEk8_0xeqr01EkJ81bgS4QyRXhja146HIbo1pSks32I3W5U6kwhSPBWTMhhp4rhfXNbzGu-oVr3KCs97Co4_kJid2PFPsa_oEa2RpVcq2Hb5wVoxwOee45oOVauEJ_I02eRigIcTrVjre8HFqtFRmn16IwF-yTXMsL5HOXCf9-xWqKHPMMdKPXvQoBbFubq2ne4cxtT36bjDgrYexgaqKAAL8_nNHW0rM", "lat": 25.7907, "lng": -80.1300},
]

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return {
        "compliance_score": "99.1%",
        "active_alerts": "01"
    }

@router.get("/properties")
def get_dashboard_properties(
    status: str = Query(None, description="Filter by zoning status"),
    db: Session = Depends(get_db)
):
    properties = MOCK_PROPERTIES
    if status:
        properties = [p for p in properties if p["zoning_status"].lower() == status.lower()]
    return properties

@router.get("/compliance/history/{property_id}")
def get_compliance_history(property_id: int, db: Session = Depends(get_db)):
    property_info = next((p for p in MOCK_PROPERTIES if p["id"] == property_id), None)
    if not property_info:
        return {"history": [], "violations": []}
    
    return {
        "property_id": property_id,
        "property_name": property_info["name"],
        "history": [
            {"date": "2026-03-15", "action": "Inspection Passed", "status": "Compliant"},
            {"date": "2026-02-10", "action": "Initial Review", "status": "Pending"},
        ],
        "violations": [
            {"date": "2026-01-20", "type": "Zoning Violation", "description": "Unauthorized rental duration", "severity": "Critical"} 
        ] if property_info["zoning_status"] == "Violation" else []
    }

@router.get("/compliance/portfolio")
def get_portfolio_compliance(db: Session = Depends(get_db)):
    return {
        "total_properties": len(MOCK_PROPERTIES),
        "compliant": len([p for p in MOCK_PROPERTIES if p["zoning_status"] == "Compliant"]),
        "pending": len([p for p in MOCK_PROPERTIES if p["zoning_status"] == "Pending"]),
        "violations": len([p for p in MOCK_PROPERTIES if p["zoning_status"] == "Violation"]),
        "properties": MOCK_PROPERTIES
    }


def _determine_eligibility_status(location: str) -> tuple[str, list[str]]:
    """Determine eligibility status based on location"""
    location_lower = location.lower()
    
    if "miami" in location_lower or "fl" in location_lower:
        return "Eligible", []
    elif "aspen" in location_lower or "co" in location_lower:
        return "Pending Review", ["Awaiting local jurisdiction confirmation"]
    else:
        return "Eligible", []


def _calculate_compliance_score(zoning_status: str, violations: list) -> float:
    """Calculate compliance score based on status and violations"""
    if zoning_status == "Compliant":
        return 100.0
    elif zoning_status == "Pending":
        return 75.0
    elif zoning_status == "Violation":
        return max(0.0, 50.0 - (len(violations) * 10))
    return 0.0


@router.get("/unified", response_model=HostDashboardResponse)
def get_unified_dashboard(
    host_id: Optional[str] = Query(None, description="Host ID to filter properties"),
    db: Session = Depends(get_db)
):
    """
    FEAT-002: Unified endpoint that returns both Address Eligibility Status 
    and Listing Health metrics for a host's dashboard.
    
    This endpoint provides a complete view of:
    - Address eligibility for each property
    - Listing health metrics (compliance score, alerts, violations)
    - Overall portfolio health
    """
    
    # In production, filter by host_id from database
    # For now, use mock data
    properties_data = MOCK_PROPERTIES
    
    unified_properties = []
    total_alerts = 0
    total_compliance = 0.0
    
    for prop in properties_data:
        # Determine eligibility status
        eligibility_status, issues = _determine_eligibility_status(prop["location"])
        
        # Parse location for address details
        location_parts = prop["location"].split(", ")
        city = location_parts[0] if len(location_parts) > 0 else ""
        state = location_parts[1] if len(location_parts) > 1 else ""
        
        # Create eligibility object
        eligibility = AddressEligibilityStatus(
            address=prop["name"],
            city=city,
            state=state,
            jurisdiction=f"{city}, {state}",
            status=eligibility_status,
            last_checked=datetime.now(),
            issues=issues
        )
        
        # Determine violations
        violations = []
        if prop["zoning_status"] == "Violation":
            violations = [
                "Unauthorized rental duration",
                "Missing required permits"
            ]
        
        # Calculate compliance score
        compliance_score = _calculate_compliance_score(prop["zoning_status"], violations)
        total_compliance += compliance_score
        
        # Count active alerts
        active_alerts = len(violations) + len(issues)
        total_alerts += active_alerts
        
        # Create health metrics object
        health = ListingHealthMetrics(
            property_id=prop["id"],
            property_name=prop["name"],
            compliance_score=compliance_score,
            zoning_status=prop["zoning_status"],
            active_alerts=active_alerts,
            last_inspection=datetime.now() if prop["zoning_status"] != "Pending" else None,
            violations=violations
        )
        
        # Create unified view
        unified_view = PropertyUnifiedView(
            property_id=prop["id"],
            property_name=prop["name"],
            location=prop["location"],
            eligibility=eligibility,
            health=health,
            image_url=prop.get("image_url")
        )
        
        unified_properties.append(unified_view)
    
    # Calculate overall compliance score
    overall_compliance = total_compliance / len(properties_data) if properties_data else 0.0
    
    return HostDashboardResponse(
        host_id=host_id,
        host_name="Demo Host" if host_id else None,
        total_properties=len(properties_data),
        overall_compliance_score=round(overall_compliance, 1),
        total_active_alerts=total_alerts,
        properties=unified_properties
    )
