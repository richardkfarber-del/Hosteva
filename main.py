from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, Base, get_db
import models
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hosteva MVP PWA API", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

class HostCreate(BaseModel):
    full_name: str
    email: str
    password: str

@app.get("/")
def read_root():
    return {"message": "Hosteva API - Ready for Mobile Client"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Hosteva API is running"}

@app.post("/api/hosts/")
def create_host(host: HostCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(host.password)
    db_host = models.Host(full_name=host.full_name, email=host.email, password_hash=hashed_password)
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host

@app.get("/wizard", response_class=HTMLResponse)
def read_wizard(request: Request):
    return templates.TemplateResponse("wizard.html", {"request": request})

@app.get("/sw.js")
def read_sw():
    file_path = os.path.join(os.path.dirname(__file__), "static", "sw.js")
    return FileResponse(file_path, media_type="application/javascript")
