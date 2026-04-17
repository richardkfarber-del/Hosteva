from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.redis import get_redis
import json
import os
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.swarm import SwarmState

router = APIRouter(prefix="/state", tags=["swarm"])

class StateUpdateRequest(BaseModel):
    ticket_id: str
    status: str
    payload: Optional[Dict[str, Any]] = None

ALLOWED_TRANSITIONS = {
    "PENDING": ["BUILDING", "FAILED"],
    "BUILDING": ["AUDITING", "QA_REVIEW", "FAILED"],
    "AUDITING": ["BUILDING", "DREAMSTATE_READY", "FAILED", "DONE", "FAILED_ESCALATED"],
    "QA_REVIEW": ["BUILDING", "DREAMSTATE_READY", "FAILED"],
    "DREAMSTATE_READY": ["DEPLOYED", "FAILED"],
    "DEPLOYED": [],
    "FAILED": ["PENDING", "BUILDING"],
    "DONE": [],
    "FAILED_ESCALATED": []
}

@router.post("/update")
async def update_state(request: StateUpdateRequest, redis_client=Depends(get_redis), db: Session = Depends(get_db)):
    # Check current state
    current_state = "PENDING"
    state_data = await redis_client.get(f"swarm:state:{request.ticket_id}")
    if state_data:
        current_state = json.loads(state_data).get("status", "PENDING")
    
    # Enforce State Transition
    if current_state in ALLOWED_TRANSITIONS and request.status not in ALLOWED_TRANSITIONS[current_state] and current_state != request.status:
        raise HTTPException(status_code=400, detail=f"Illegal state transition from {current_state} to {request.status}")

    if request.status == "DREAMSTATE_READY":
        if not request.payload or "security_audit" not in request.payload:
            raise HTTPException(status_code=400, detail="Transition to DREAMSTATE_READY blocked: Missing security audit payload.")
        
        expected_token = os.environ.get("DREAMSTATE_TOKEN")
        if not expected_token:
            raise HTTPException(status_code=500, detail="DREAMSTATE_TOKEN is not configured.")
        if request.payload.get("security_audit") != expected_token:
            raise HTTPException(status_code=403, detail="Transition to DREAMSTATE_READY blocked: Invalid security token.")

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
@router.post("/submit")
async def submit_task(request: StateUpdateRequest, redis_client=Depends(get_redis)):
    data = request.model_dump()
    await redis_client.xadd("swarm:stream:tasks", {"payload": json.dumps(data)})
    return {"status": "success", "ticket_id": request.ticket_id}
