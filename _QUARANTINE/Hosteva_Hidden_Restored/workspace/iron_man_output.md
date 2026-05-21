I have refactored `app/routers/listings.py` to remove the legacy `celery` dependency and instead use `fastapi.BackgroundTasks` natively, per the requirements in `BUG-001_celery_removal.md`.

```python
# FILE: app/routers/listings.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.oauth import OAuthConnection, PropertyListing
from app.models.property import Property
import uuid

router = APIRouter(prefix="/listings", tags=["listings"])

def sync_property_to_otas(property_id: str):
    # Dummy async task mechanic
    # 1. Load property data
    # 2. Assemble JSON payload based on spike
    # 3. Load valid OAuth tokens
    # 4. Dispatch requests to Airbnb/VRBO
    pass

@router.post("/generate/{property_id}")
def generate_listing(property_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Verify property exists
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Trigger background task for OTA sync via FastAPI BackgroundTasks
    background_tasks.add_task(sync_property_to_otas, property_id)
    
    return {"message": "Listing generation initiated and syncing to OTAs"}

@router.get("/{property_id}/status")
def get_listing_status(property_id: str, db: Session = Depends(get_db)):
    listings = db.query(PropertyListing).filter(PropertyListing.property_id == property_id).all()
    return {"property_id": property_id, "listings": listings}
```