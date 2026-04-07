from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

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
