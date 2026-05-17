from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/v1", tags=["properties"])

class PropertyResponse(BaseModel):
    property_id: str
    owner_name: str
    address: str

class PropertiesListResponse(BaseModel):
    data: List[PropertyResponse]

@router.get("/properties", response_model=PropertiesListResponse)
async def get_properties(
    authorization: Optional[str] = Header(None), 
    simulate_timeout: bool = Query(False)
):
    """
    Retrieve property data. 
    Enforces strict PII masking on owner_name and address.
    """
    if not authorization or authorization != "Bearer valid-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if simulate_timeout:
        raise HTTPException(status_code=503, detail="Service Unavailable - Timeout")
        
    # Positive response with PII masked to enforce privacy boundaries
    return PropertiesListResponse(
        data=[
            PropertyResponse(
                property_id="123",
                owner_name="J*** D**",
                address="123 M*** St"
            )
        ]
    )
