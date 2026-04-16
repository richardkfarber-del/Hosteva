from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
)

class Analytics(BaseModel):
    total_queries: int
    quota_remaining: int

class RecentQuery(BaseModel):
    query_id: str
    timestamp: datetime
    summary: str

class DashboardOverview(BaseModel):
    user_id: str
    subscription_tier: str
    analytics: Analytics
    recent_queries: List[RecentQuery]

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview():
    # Mocking user logic
    return DashboardOverview(
        user_id="mock_user_123",
        subscription_tier="Pro",
        analytics=Analytics(
            total_queries=150,
            quota_remaining=850
        ),
        recent_queries=[
            RecentQuery(
                query_id="q_001",
                timestamp=datetime.now(),
                summary="Sample summary query 1"
            )
        ]
    )
