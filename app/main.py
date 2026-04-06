from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routers import zoning, compliance, hosts
import os

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

# Task 5: Serve landing.html as the root URL
@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("templates/landing.html")

# Task 4: Serve wizard.html
@app.get("/wizard", include_in_schema=False)
def read_wizard():
    return FileResponse("templates/wizard.html")
