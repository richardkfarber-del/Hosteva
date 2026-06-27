from fastapi import FastAPI, Request, Response, Depends, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.routers import user, listings, ordinances, zoning, compliance, hosts, properties, notifications, dashboard_api, eligibility, florida_compliance, listing_optimizer, permit_generator, recommendations, subscriptions, documents, market_intelligence, pricing
from app.integrations.ota_routes import router as ota_router
from app.api.routes import swarm, queue, properties as v1_properties
from app.api.v1.onboarding.validate import router as validate_router
from app.api.v1.compliance import router as compliance_v1_router
from app.api.v1.billing import router as billing_v1_router
from app.api.v1.operations import router as operations_v1_router
from app.api.v1.inbox import router as inbox_v1_router



from app.schemas.dashboard import HostDashboardResponse
import os
import traceback
import requests
from dotenv import load_dotenv

load_dotenv()

templates = Jinja2Templates(directory="app/templates")

SHOW_DOCS = os.getenv("SHOW_DOCS", "True").lower() == "true"

def import_models():
    # Explicitly import all database models so they register on Base and relationships are mapped
    import app.db_models
    import app.models.memory
    import app.models.host
    import app.models.property
    import app.models.zoning
    import app.models.job
    import app.models.compliance
    import app.models.swarm
    import app.models.oauth
    import app.integrations.ota_models

# Register models to ensure mapping metadata is configured correctly
import_models()

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
    # Defensive programming: Ensure request.state has user initialized to None if not present
    if not hasattr(request.state, "user"):
        request.state.user = None
        
    try:
        response = await call_next(request)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

    if response is not None and hasattr(response, "headers"):
        # Vibranium Habit: Strict-Transport-Security and other browser security headers applied globally
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        content_type = response.headers.get("content-type", "")
        if content_type and "text/html" in content_type.lower():
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
    return response

os.makedirs("app/static/property_images", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/sw.js", include_in_schema=False)
def serve_sw():
    return FileResponse("app/static/sw.js", media_type="application/javascript")

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
app.include_router(validate_router)
app.include_router(compliance_v1_router)
app.include_router(billing_v1_router)
app.include_router(operations_v1_router)
app.include_router(inbox_v1_router)





def get_optional_user_cookie(access_token: Optional[str] = Cookie(None)) -> Optional[dict]:
    if not access_token:
        return None
    try:
        from app.core.security import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is not None:
            return {"username": username, "role": payload.get("role", "host")}
    except Exception:
        pass
    return None

@app.get("/", include_in_schema=False)
def read_root(request: Request, user: Optional[dict] = Depends(get_optional_user_cookie)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
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
    res = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )
    res.delete_cookie(key="access_token", path="/")
    return res

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
def read_dashboard(request: Request, address: Optional[str] = None):
    # Verify cookie-based JWT access token to protect dashboard from 500 errors
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    try:
        from app.core.security import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return RedirectResponse(url="/login", status_code=303)
    except Exception:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={"request": request, "google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("Maps_API_KEY") or "", "active_page": "dashboard"}
    )

@app.get("/manage/{property_id}", name="manage_property")
def read_manage_property(property_id: str, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    try:
        from app.core.security import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return RedirectResponse(url="/login", status_code=303)
    except Exception:
        return RedirectResponse(url="/login", status_code=303)

    from app.models.property import Property
    from app.models.host import Host
    host = db.query(Host).filter(Host.username == username).first()
    if not host:
        return RedirectResponse(url="/login", status_code=303)
        
    property_item = db.query(Property).filter(Property.id == property_id, Property.user_id == host.id).first()
    if not property_item:
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="manage.html", 
        context={
            "request": request, 
            "property_id": property_id, 
            "property_address": property_item.address,
            "google_maps_api_key": os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("Maps_API_KEY") or "", 
            "active_page": "dashboard"
        }
    )

@app.get("/dashboard/tasks/{task_id}", name="task_detail")
def read_task_detail(task_id: str, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    try:
        from app.core.security import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return RedirectResponse(url="/login", status_code=303)
    except Exception:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="task_detail.html",
        context={"request": request, "task_id": task_id, "active_page": "compliance"}
    )

from app.core.security import get_current_user
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)

