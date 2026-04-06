from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, Base, get_db
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hosteva MVP JSON API", version="1.0.0")

class HostCreate(BaseModel):
    full_name: str
    email: str
    password_hash: str

@app.get("/")
def read_root():
    return {"message": "Hosteva API - Ready for Mobile Client"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Hosteva API is running"}

@app.post("/api/hosts/")
def create_host(host: HostCreate, db: Session = Depends(get_db)):
    db_host = models.Host(full_name=host.full_name, email=host.email, password_hash=host.password_hash)
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host

from fastapi.responses import HTMLResponse
import os

@app.get("/wizard", response_class=HTMLResponse)
def read_wizard():
    file_path = os.path.join(os.path.dirname(__file__), "templates", "wizard.html")
    with open(file_path, "r") as f:
        return f.read()
