from fastapi import FastAPI, Request, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from app.routers import user, listings, ordinances, zoning, compliance, hosts, properties, notifications, dashboard_api, eligibility, florida_compliance, listing_optimizer, permit_generator, recommendations, subscriptions, documents, market_intelligence, pricing
from app.integrations.ota_routes import router as ota_router
from app.api.routes import swarm, queue, properties as v1_properties
from app.schemas.dashboard import HostDashboardResponse
import os
import traceback
import requests
from dotenv import load_dotenv

load_dotenv()

templates = Jinja2Templates(directory="app/templates")

SHOW_DOCS = os.getenv("SHOW_DOCS", "True").lower() == "true"

app = FastAPI(
    title="Hosteva Zoning and Compliance Engine",
    docs_url="/docs" if SHOW_DOCS else None,
    redoc_url="/redoc" if SHOW_DOCS else None
)

# Vibranium Habit: Strictly lock down Cross-Origin Resource Sharing (CORS)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://app.hosteva.com,https://api.hosteva.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, # Vibranium Habit: Never fallback to wildcard
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Enforce Vibranium Habit: Require HTTPS in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Vibranium Habit: Strict-Transport-Security and other browser security headers applied globally
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse(str(traceback.format_exc()), status_code=500)

app.include_router(listings.router)
app.include_router(zoning.router)
app.include_router(ordinances.router)
app.include_router(compliance.router)
app.include_router(hosts.router)
app.include_router(user.router)
app.include_router(properties.router)
app.include_router(v1_properties.router)
app.include_router(notifications.router)
app.include_router(dashboard_api.router)
app.include_router(eligibility.router)
app.include_router(florida_compliance.router)
app.include_router(listing_optimizer.router)
app.include_router(permit_generator.router)
app.include_router(recommendations.router)
app.include_router(subscriptions.router, prefix="/api")
app.include_router(pricing.router)
app.include_router(documents.router, prefix="/api")
app.include_router(market_intelligence.router)
app.include_router(ota_router)
app.include_router(swarm.router)
app.include_router(queue.router)

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

@app.get("/login", include_in_schema=False)
def read_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )

@app.get("/register", include_in_schema=False)
def read_register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request}
    )

@app.get("/integrations", include_in_schema=False)
def read_integrations(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="integrations.html",
        context={"request": request, "active_page": "integrations"}
    )

@app.get("/dashboard", name="dashboard")
def read_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={"request": request, "google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY", ""), "active_page": "dashboard"}
    )

from app.core.security import get_current_user
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.host import Host

@app.get("/users/me")
@app.get("/api/v1/users/me")
def get_current_active_user_proxy(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    username = current_user.get("username")
    host = db.query(Host).filter(Host.username == username).first()
    if not host:
        return {"username": "Guest", "email": "", "full_name": "Guest", "tier": "Free Tier"}
    
    sub_tier = "Free Tier"
    if host.subscription and host.subscription.status == "active":
        sub_tier = host.subscription.plan_details or "Pro"
        if isinstance(sub_tier, str):
            sub_tier = sub_tier.capitalize() + " Host"
        else:
            sub_tier = "Pro Host"
            
    return {
        "id": host.id,
        "username": host.username,
        "email": host.email,
        "full_name": host.username,
        "tier": sub_tier
    }
