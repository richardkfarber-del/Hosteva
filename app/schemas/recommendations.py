from pydantic import BaseModel
from typing import List, Optional


class Recommendation(BaseModel):
    """Individual recommendation with priority and category"""
    category: str  # e.g., "pricing", "availability", "photos", "description"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    impact: str  # Expected impact description
    
    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    """Request to generate recommendations for a property"""
    property_id: str
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Response containing generated recommendations"""
    property_id: str
    overall_health_score: float
    recommendations: List[Recommendation]
    summary: str
    
    class Config:
        from_attributes = True
