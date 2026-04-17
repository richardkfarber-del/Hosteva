from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/overview")
async def get_dashboard_overview():
    return {
        "user_subscription_tier": "pro",
        "analytics_quota_remaining": 850,
        "recent_query_history": [
            {"query_id": "q1", "timestamp": "2023-10-01T12:00:00Z", "status": "success"},
            {"query_id": "q2", "timestamp": "2023-10-01T12:05:00Z", "status": "success"}
        ]
    }
