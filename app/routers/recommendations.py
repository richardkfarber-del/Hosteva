from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recommendations import (
    RecommendationRequest,
    RecommendationResponse,
    Recommendation
)
from app.services.recommendations import RecommendationEngineService

router = APIRouter(
    prefix="/api/recommendation-engine",
    tags=["Recommendation Engine"]
)


@router.post("/generate", response_model=RecommendationResponse)
def generate_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate actionable recommendations to improve listing performance.
    
    Analyzes listing metrics and provides prioritized suggestions for:
    - Pricing optimization
    - Photo quality and quantity
    - Response time improvements
    - Calendar availability
    - Description enhancements
    - Amenity additions
    - Guest experience improvements
    
    Returns recommendations sorted by priority (high, medium, low) with
    expected impact estimates.
    """
    service = RecommendationEngineService()
    result = service.generate_recommendations(request.property_id)
    
    return RecommendationResponse(
        property_id=result["property_id"],
        overall_health_score=result["overall_health_score"],
        recommendations=[Recommendation(**rec) for rec in result["recommendations"]],
        summary=result["summary"]
    )
