from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class HostBase(BaseModel):
    username: str = Field(..., max_length=50, pattern=r"^[a-zA-Z0-9_\-]+$")
    email: EmailStr = Field(..., max_length=100)

class HostCreate(HostBase):
    password: str = Field(..., max_length=128)

class HostResponse(HostBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
