from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.database import engine, Base
from app.routers import zoning, compliance, hosts, properties, notifications, dashboard_api, eligibility
from app.models.property import Property
import os

templates = Jinja2Templates(directory="templates")

# Create tables
Base.metadata.create_all(bind=engine)

# Disable docs in production-like environment if needed
SHOW_DOCS = os.getenv("SHOW_DOCS", "True").lower() == "true"

app = FastAPI(
    title="Hosteva Zoning and Compliance Engine",
    description="FastAPI Backend for Zoning and Compliance Engines.",
    docs_url="/docs" if SHOW_DOCS else None,
    redoc_url="/redoc" if SHOW_DOCS else None
)

app.include_router(zoning.router)
app.include_router(compliance.router)
app.include_router(hosts.router)
app.include_router(properties.router)
app.include_router(notifications.router)
app.include_router(dashboard_api.router)
app.include_router(eligibility.router)

# Task 5: Serve landing.html as the root URL
@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("templates/landing.html")

# Task 4: Serve wizard.html
@app.get("/wizard", include_in_schema=False)
def read_wizard():
    return FileResponse("templates/wizard.html")

@app.get('/dashboard', include_in_schema=False)
def read_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html", 
        context={"request": request, "google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY", "")}
    )
