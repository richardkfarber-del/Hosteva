from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.host import Host
from app.core.security import get_current_user

router = APIRouter(prefix="/api/user", tags=["User"])

@router.get("/analytics")
def get_user_analytics(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    username = current_user.get("username")  # Fixed BOLA vulnerability
    host = db.query(Host).filter(Host.username == username).first()
    
    if not host:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "subscription_tier": getattr(host, "subscription_tier", "Pro"),
        "recent_queries": [
            {"query": "What are the STR laws in Miami?", "date": "2026-04-10"},
            {"query": "Do I need a permit for Aspen?", "date": "2026-04-11"},
            {"query": "Is a 30-day minimum stay required in Orlando?", "date": "2026-04-12"}
        ]
    }
