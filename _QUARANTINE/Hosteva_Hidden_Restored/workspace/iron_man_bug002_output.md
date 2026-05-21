```python
# FILE: app/routers/listings.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.oauth import OAuthConnection, PropertyListing
from app.models.property import Property
from app.core.security import get_current_user
import uuid

router = APIRouter(prefix="/listings", tags=["listings"])

def sync_property_to_otas(property_id: str):
    # Dummy async task mechanic
    # 1. Load property data
    # 2. Assemble JSON payload based on spike
    # 3. Load valid OAuth tokens
    # 4. Dispatch requests to Airbnb/VRBO
    print(f"Syncing property {property_id} to OTAs (Pending implementation)...")

@router.post("/generate/{property_id}")
def generate_listing(property_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verify property exists
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Verify ownership to prevent IDOR
    if prop.user_id != current_user.get("username"):
        raise HTTPException(status_code=403, detail="Not authorized to access this property")
        
    # Trigger background task for OTA sync via FastAPI BackgroundTasks
    background_tasks.add_task(sync_property_to_otas, property_id)
    
    return {"message": "Listing generation initiated and syncing to OTAs"}

@router.get("/{property_id}/status")
def get_listing_status(property_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verify ownership to prevent IDOR
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    if prop.user_id != current_user.get("username"):
        raise HTTPException(status_code=403, detail="Not authorized to access this property")

    listings = db.query(PropertyListing).filter(PropertyListing.property_id == property_id).all()
    return {"property_id": property_id, "listings": listings}
```

```python
# FILE: app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from app.database import engine, Base
from app.routers import listings, ordinances, zoning, compliance, hosts, properties, notifications, dashboard_api, eligibility, florida_compliance, listing_optimizer, permit_generator, recommendations, subscriptions, documents
from app.integrations.ota_routes import ota_router
from app.schemas.dashboard import HostDashboardResponse
import os
import traceback
import requests

templates = Jinja2Templates(directory="templates")

SHOW_DOCS = os.getenv("SHOW_DOCS", "True").lower() == "true"

app = FastAPI(
    title="Hosteva Zoning and Compliance Engine",
    docs_url="/docs" if SHOW_DOCS else None,
    redoc_url="/redoc" if SHOW_DOCS else None
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse(str(traceback.format_exc()), status_code=500)

app.include_router(listings.router)
app.include_router(zoning.router)
app.include_router(ordinances.router)
app.include_router(compliance.router)
app.include_router(hosts.router)
app.include_router(properties.router)
app.include_router(notifications.router)
app.include_router(dashboard_api.router)
app.include_router(eligibility.router)
app.include_router(florida_compliance.router)
app.include_router(listing_optimizer.router)
app.include_router(permit_generator.router)
app.include_router(recommendations.router)
app.include_router(subscriptions.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(ota_router)

@app.get("/", include_in_schema=False)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="landing.html", 
        context={"request": request}
    )

@app.get("/wizard", include_in_schema=False)
def read_wizard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="wizard.html",
        context={"request": request, "active_page": "compliance"}
    )



@app.get('/dashboard', name="dashboard")
def read_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={"request": request, "google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY", ""), "active_page": "dashboard"}
    )
```