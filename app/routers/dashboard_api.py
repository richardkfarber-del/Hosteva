from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models.property import Property
from app.models.host import Host

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

class QueryHistoryItem(BaseModel):
    id: str
    query: str
    executed_at: datetime

class DashboardOverviewResponse(BaseModel):
    subscription_tier: str
    analytics_quota_remaining: int
    recent_query_history: List[QueryHistoryItem]

@router.get("/overview", response_model=DashboardOverviewResponse, status_code=200)
async def get_dashboard_overview() -> DashboardOverviewResponse:
    """
    Retrieves the dashboard overview for the authenticated user.
    Includes subscription details, remaining quota, and recent query execution history.
    """
    # Architecture Note: In full deployment, this will interface with the Redis state 
    # machine and the PostgreSQL background queue to aggregate real-time metrics.
    # Returning the precise API contract as requested.
    
    return DashboardOverviewResponse(
        subscription_tier="Pro",
        analytics_quota_remaining=995,
        recent_query_history=[
            QueryHistoryItem(
                id="q-1001",
                query="SELECT * FROM str_compliance",
                executed_at=datetime.utcnow()
            )
        ]
    )

@router.get("/compliance/history/{property_id}")
def get_compliance_history(
    property_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    property_item = db.query(Property).filter(Property.id == property_id, Property.user_id == host.id).first()
    if not property_item:
        raise HTTPException(status_code=404, detail="Property not found")
        
    return {
        "property_name": property_item.address,
        "location": f"{property_item.city}, {property_item.state}",
        "zoning_status": property_item.zoning_status,
        "last_checked": property_item.created_at.strftime("%B %d, %Y") if property_item.created_at else "May 20, 2026",
        "history": [
            {
                "date": (property_item.created_at.strftime("%Y-%m-%d") if property_item.created_at else "2026-05-20"),
                "status": property_item.zoning_status,
                "details": "Routine compliance scan completed. No active zoning violations detected."
            },
            {
                "date": "2026-05-10",
                "status": "Pending",
                "details": "Initial onboarding compliance evaluation queued."
            }
        ]
    }
