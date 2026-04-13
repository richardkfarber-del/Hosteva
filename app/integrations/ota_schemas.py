from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# --- OTA Integration Schemas ---

class OtaIntegrationBase(BaseModel):
    platform_name: str = Field(..., description="The name of the OTA platform (e.g., 'airbnb', 'vrbo')")

class OtaIntegrationCreate(OtaIntegrationBase):
    """Schema for securely receiving tokens before database encryption"""
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    listing_id: Optional[int] = None

class OtaIntegrationResponse(OtaIntegrationBase):
    """
    Response schema. 
    Vibranium Standard Compliance: OAuth tokens are strictly excluded from egress schemas.
    """
    id: int
    listing_id: Optional[int] = None
    token_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Hosteva Listing Schemas ---

class HostevaListingBase(BaseModel):
    property_address: str
    compliance_status: Optional[str] = "pending"
    base_price: Optional[float] = None

class HostevaListingCreate(HostevaListingBase):
    user_id: int

class HostevaListingResponse(HostevaListingBase):
    id: int
    user_id: int
    integrations: List[OtaIntegrationResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)