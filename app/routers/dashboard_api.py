from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Mock dynamic data pulling from DB logic
    return {
        "compliance_score": "99.1%",
        "active_alerts": "01"
    }
