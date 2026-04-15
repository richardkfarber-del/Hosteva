from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.redis import get_redis
import json
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.swarm import SwarmState

router = APIRouter(prefix="/state", tags=["swarm"])

class StateUpdateRequest(BaseModel):
    ticket_id: str
    status: str
    payload: Optional[Dict[str, Any]] = None

@router.post("/update")
async def update_state(request: StateUpdateRequest, redis_client=Depends(get_redis), db: Session = Depends(get_db)):
    await redis_client.set(f"swarm:state:{request.ticket_id}", request.model_dump_json())
    try:
        db.merge(SwarmState(ticket_id=request.ticket_id, status=request.status, payload=request.payload))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success", "ticket_id": request.ticket_id, "new_status": request.status}

@router.get("/status/{ticket_id}")
async def get_status(ticket_id: str, redis_client=Depends(get_redis)):
    data = await redis_client.get(f"swarm:state:{ticket_id}")
    if data:
        return json.loads(data)
    return {"ticket_id": ticket_id, "status": "PENDING"}