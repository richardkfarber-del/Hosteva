from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.listing_optimizer import (
    ListingSyncRequest,
    BatchListingSyncRequest,
    ListingSyncResponse,
    BatchListingSyncResponse
)
from app.services.listing_optimizer import ListingOptimizerService

router = APIRouter(
    prefix="/api/listing-optimizer",
    tags=["Listing Optimizer"]
)

@router.post("/sync", response_model=ListingSyncResponse)
def sync_single_listing(request: ListingSyncRequest):
    """
    Synchronize a single listing from Airbnb or VRBO.
    
    This endpoint implements FEAT-004: Listing Optimizer Integration.
    """
    service = ListingOptimizerService()
    
    platform = request.platform.lower()
    
    if platform == "airbnb":
        result = service.sync_airbnb_listing(request.listing_id)
    elif platform == "vrbo":
        result = service.sync_vrbo_listing(request.listing_id)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {platform}. Supported platforms: airbnb, vrbo"
        )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    
    return result

@router.post("/sync/batch", response_model=BatchListingSyncResponse)
def sync_multiple_listings(request: BatchListingSyncRequest):
    """
    Synchronize multiple listings from various platforms in a single request.
    
    This endpoint implements FEAT-004: Listing Optimizer Integration.
    """
    service = ListingOptimizerService()
    
    # Convert request listings to dict format
    listings = [
        {"platform": listing.platform, "listing_id": listing.listing_id}
        for listing in request.listings
    ]
    
    results = service.sync_all_listings(listings)
    
    successful = sum(1 for r in results if r.get("status") != "error")
    failed = len(results) - successful
    
    return {
        "results": results,
        "total_synced": len(results),
        "successful": successful,
        "failed": failed
    }

@router.post("/sync/background", status_code=202)
def sync_listings_background(
    request: BatchListingSyncRequest,
    background_tasks: BackgroundTasks
):
    """
    Queue listing synchronization to run in the background.
    Returns immediately with accepted status.
    """
    def sync_task():
        service = ListingOptimizerService()
        listings = [
            {"platform": listing.platform, "listing_id": listing.listing_id}
            for listing in request.listings
        ]
        service.sync_all_listings(listings)
    
    background_tasks.add_task(sync_task)
    
    return {
        "status": "accepted",
        "message": f"Queued {len(request.listings)} listings for synchronization",
        "total_listings": len(request.listings)
    }

@router.get("/platforms")
def get_supported_platforms():
    """
    Get list of supported listing platforms and their capabilities.
    """
    return {
        "supported_platforms": ["airbnb", "vrbo"],
        "capabilities": {
            "airbnb": {
                "metrics": [
                    "overall_score",
                    "response_rate",
                    "response_time_minutes",
                    "acceptance_rate",
                    "cancellation_rate",
                    "review_score",
                    "total_reviews",
                    "booking_rate",
                    "occupancy_rate"
                ]
            },
            "vrbo": {
                "metrics": [
                    "overall_score",
                    "inquiry_response_rate",
                    "average_response_time_hours",
                    "booking_conversion_rate",
                    "review_rating",
                    "total_reviews",
                    "calendar_accuracy",
                    "occupancy_rate"
                ]
            }
        }
    }
