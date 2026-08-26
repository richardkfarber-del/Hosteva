```python
# FILE: app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from app.database import engine, Base
from app.routers import listings, ordinances, zoning, compliance, hosts, properties, notifications, dashboard_api, eligibility, florida_compliance, listing_optimizer, permit_generator, recommendations, subscriptions, documents
from app.integrations.ota_routes import router as ota_router
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