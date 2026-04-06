from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

@router.post("/simulate_status_change")
async def simulate_status_change(host_email: str, property_id: str, old_status: str, new_status: str):
    payload = {
        "host_email": host_email,
        "property_id": property_id,
        "old_status": old_status,
        "new_status": new_status
    }
    try:
        with open("/tmp/email_queue.json", "w") as f:
            json.dump(payload, f)
        return {"status": "success", "message": "Event fired"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))