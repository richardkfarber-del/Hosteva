from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, Base, get_db
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hosteva MVP API", version="1.0.0")

class HostCreate(BaseModel):
    full_name: str
    email: str
    password_hash: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Hosteva MVP - Shield Protocol Active."}

@app.get("/wizard", response_class=HTMLResponse)
def preview_wizard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hosteva - Add Property Wizard (Preview)</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            body { font-family: 'Inter', sans-serif; background-color: #F5F5F5; margin: 0; padding: 20px; color: #1B3A5F; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { color: #1B3A5F; font-weight: 700; letter-spacing: -0.02em; }
            
            /* 30-degree pitch motif using clip-path */
            .property-card {
                background: #FFFFFF;
                max-width: 400px;
                margin: 0 auto;
                padding: 30px;
                border: 1px solid #E0E0E0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                /* Top-right corner cut at ~30 degrees */
                clip-path: polygon(0 0, calc(100% - 30px) 0, 100% 17px, 100% 100%, 0 100%);
                border-radius: 8px;
                border-top-right-radius: 0;
            }
            .shield-badge {
                display: inline-block;
                background-color: #3CB4C4;
                color: #fff;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .btn-primary {
                display: block;
                width: 100%;
                background-color: #2B8FAD;
                color: #FFFFFF;
                border: none;
                padding: 14px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
                cursor: pointer;
                margin-top: 20px;
                box-shadow: 0 2px 4px rgba(43, 143, 173, 0.3);
            }
            .btn-primary:hover { background-color: #1B3A5F; }
            .stitch-ref { margin-top: 30px; font-size: 12px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Hosteva</h1>
        </div>
        <div class="property-card">
            <div class="shield-badge">🛡️ Zoning Verification</div>
            <h2>Add Property</h2>
            <p>Enter the property location to verify zoning compliance automatically.</p>
            <input type="text" placeholder="123 Ocean Drive, Miami, FL" style="width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; margin-bottom: 10px;">
            <button class="btn-primary">Verify Location</button>
            <div class="stitch-ref">
                Design References: STITCH-HSTV-ADDPROP-992A | STITCH-HSTV-COMPLIANCE-774B
            </div>
        </div>
    </body>
    </html>
    """

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
