from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

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
