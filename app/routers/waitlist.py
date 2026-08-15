from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db, Base, engine
from app.db_models import WaitlistLead
import datetime

router = APIRouter(prefix="/api/v1/waitlist", tags=["waitlist"])

CBaseModel = BaseModel

class WaitlistRequest(BaseModel):
    email: str
    portfolio_size: Optional[str] = "1-2"
    tier_interest: Optional[str] = "PHASE_2_AUTOMATION"

@router.post("/", status_code=status.HTTP_201_CREATED)
@router.post("", status_code=status.HTTP_201_CREATED)
def join_waitlist(payload: WaitlistRequest, db: Session = Depends(get_db)):
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="A valid email address is required.")
    
    lead = WaitlistLead(
        email=payload.email.strip().lower(),
        portfolio_size=payload.portfolio_size or "1-2",
        tier_interest=payload.tier_interest or "PHASE_2_AUTOMATION",
        created_at=datetime.datetime.utcnow()
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {
        "status": "success",
        "message": "Thank you for joining the Phase II Automation Suite waitlist! We will notify you when access opens.",
        "id": lead.id
    }
