from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from app.database import engine, Base
from app.routers import zoning, compliance, hosts, properties, notifications, dashboard_api, eligibility, florida_compliance, listing_optimizer, permit_generator, recommendations
from app.schemas.dashboard import HostDashboardResponse
import os
import traceback
import requests

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

SHOW_DOCS = os.getenv("SHOW_DOCS", "True").lower() == "true"

app = FastAPI(
    title="Hosteva Zoning and Compliance Engine",
    docs_url="/docs" if SHOW_DOCS else None,
    redoc_url="/redoc" if SHOW_DOCS else None
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse(str(traceback.format_exc()), status_code=500)

app.include_router(zoning.router)
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

@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("templates/landing.html")

@app.get("/wizard", include_in_schema=False)
def read_wizard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="wizard.html",
        context={"request": request, "active_page": "compliance"}
    )

from pydantic import BaseModel
class AddressQuery(BaseModel):
    address: str

@app.post("/wizard/audit", include_in_schema=False)
def perform_audit(query: AddressQuery):
    address = query.address.lower()
    
    # Simulate Pass/Fail
    if "fl" in address or "florida" in address:
        status = "Pass"
        message = "Address is eligible. Form HR-7020 and standard safety requirements met."
        details = [
            "Fire Extinguisher verified",
            "Smoke alarms functional",
            "Form HR-7020 on file"
        ]
    else:
        status = "Fail"
        message = "Address not in a supported Florida jurisdiction or incomplete."
        details = ["Missing Florida State Permit"]
        
    return {
        "status": status,
        "message": message,
        "details": details
    }

@app.get('/dashboard')
def read_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={"request": request, "google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY", ""), "active_page": "dashboard"}
    )
