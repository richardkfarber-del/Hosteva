from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ListingSyncRequest(BaseModel):
    platform: str = Field(..., description="Platform name: 'airbnb' or 'vrbo'")
    listing_id: str = Field(..., description="Platform-specific listing identifier")

class BatchListingSyncRequest(BaseModel):
    listings: List[ListingSyncRequest] = Field(..., description="List of listings to sync")

class HealthMetrics(BaseModel):
    overall_score: Optional[float] = None
    response_rate: Optional[float] = None
    response_time_minutes: Optional[int] = None
    average_response_time_hours: Optional[float] = None
    acceptance_rate: Optional[float] = None
    inquiry_response_rate: Optional[float] = None
    cancellation_rate: Optional[float] = None
    booking_conversion_rate: Optional[float] = None
    review_score: Optional[float] = None
    review_rating: Optional[float] = None
    total_reviews: Optional[int] = None
    booking_rate: Optional[float] = None
    occupancy_rate: Optional[float] = None
    calendar_accuracy: Optional[float] = None

class ListingSyncResponse(BaseModel):
    listing_id: str
    platform: str
    health_metrics: Optional[HealthMetrics] = None
    listing_status: Optional[str] = None
    last_booking_date: Optional[str] = None
    next_available_date: Optional[str] = None
    synced_at: str
    status: Optional[str] = None
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "listing_id": "12345",
                "platform": "airbnb",
                "health_metrics": {
                    "overall_score": 85,
                    "response_rate": 95,
                    "review_score": 4.7
                },
                "listing_status": "active",
                "synced_at": "2026-04-11T12:00:00"
            }
        }

class BatchListingSyncResponse(BaseModel):
    results: List[ListingSyncResponse]
    total_synced: int
    successful: int
    failed: int
