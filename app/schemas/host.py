from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class HostBase(BaseModel):
    username: str = Field(..., max_length=50, pattern="^[a-zA-Z0-9_\-]+$")
    email: EmailStr = Field(..., max_length=100)

class HostCreate(HostBase):
    password: str = Field(..., min_length=8, max_length=100) # Task 3: Payload size limits

class HostResponse(HostBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
