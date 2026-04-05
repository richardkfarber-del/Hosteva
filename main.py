from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, Base, get_db
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hosteva MVP API", version="1.0.0")
templates = Jinja2Templates(directory="templates")

class HostCreate(BaseModel):
    full_name: str
    email: str
    password_hash: str

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/wizard", response_class=HTMLResponse)
def preview_wizard(request: Request):
    return templates.TemplateResponse("wizard.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def preview_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Hosteva API is running"}

@app.post("/hosts/")
def create_host(host: HostCreate, db: Session = Depends(get_db)):
    db_host = models.Host(full_name=host.full_name, email=host.email, password_hash=host.password_hash)
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host
