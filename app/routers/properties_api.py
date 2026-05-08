from fastapi import APIRouter, Header, HTTPException
from typing import Optional

router = APIRouter(prefix="/api/v1", tags=["properties"])

@router.get("/properties")
async def get_properties(authorization: Optional[str] = Header(None), simulate_timeout: bool = False):
    if not authorization or authorization != "Bearer valid-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if simulate_timeout:
        raise HTTPException(status_code=503, detail="Service Unavailable - Timeout")
        
    return {
        "data": [
            {
                "property_id": "123",
                "owner_name": "J*** D**",
                "address": "123 M*** St"
            }
        ]
    }
