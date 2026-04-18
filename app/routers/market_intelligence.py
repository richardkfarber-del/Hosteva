from fastapi import APIRouter, HTTPException, Depends
from app.schemas.market_intelligence import MarketIntelligenceRequest, MarketIntelligenceResponse

router = APIRouter(
    prefix="/api/v1/market",
    tags=["Market Intelligence"]
)

@router.post("/estimate", response_model=MarketIntelligenceResponse)
def get_market_estimate(request: MarketIntelligenceRequest):
    # Mock integration with AirDNA/Mashvisor
    try:
        # Here we would normally make a requests.get() to the AirDNA API
        # Example: requests.get(f"https://api.airdna.co/v1/market/property?lat={request.latitude}&lng={request.longitude}")
        
        # Simulating a mock response for now
        base_rate = 150.0 + (request.bedrooms * 50)
        occupancy = 0.65
        annual_revenue = base_rate * 365 * occupancy
        
        return MarketIntelligenceResponse(
            average_daily_rate=base_rate,
            occupancy_rate=occupancy,
            estimated_annual_revenue=annual_revenue,
            market_score=85,
            source="AirDNA (Mock)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
