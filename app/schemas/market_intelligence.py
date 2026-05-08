from pydantic import BaseModel
from typing import Optional

class MarketIntelligenceRequest(BaseModel):
    latitude: float
    longitude: float
    property_type: Optional[str] = "entire_home"
    bedrooms: Optional[int] = 1

class MarketIntelligenceResponse(BaseModel):
    average_daily_rate: float
    occupancy_rate: float
    estimated_annual_revenue: float
    market_score: int
    source: str
