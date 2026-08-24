import os
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.host import Host
from app.core.security import get_current_user, verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/api/user", tags=["User"])

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_username = db.query(Host).filter(Host.username == user_data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = db.query(Host).filter(Host.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed = get_password_hash(user_data.password)
    new_host = Host(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed
    )
    db.add(new_host)
    db.commit()
    db.refresh(new_host)
    return {"status": "success", "username": new_host.username}

@router.post("/login")
def login_user(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    host = db.query(Host).filter(
        (Host.username == form_data.username) | 
        (Host.email == form_data.username)
    ).first()
    if not host or not verify_password(form_data.password, host.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    access_token = create_access_token(data={"sub": host.username, "role": "host"})
    is_production = os.getenv("ENVIRONMENT", "").lower() == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        path="/",
        max_age=1800,
        samesite="lax",
        secure=is_production,  # HTTPS-only cookies in production
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        username = current_user.get("username") if current_user else "Guest"
        host = db.query(Host).filter(Host.username == username).first() if username != "Guest" else None
        if not host:
            return {
                "id": "guest_id",
                "username": "Guest",
                "email": "",
                "full_name": "Guest",
                "tier": "Free Tier"
            }
            
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
    except Exception:
        return {
            "id": "guest_id",
            "username": "Guest",
            "email": "",
            "full_name": "Guest",
            "tier": "Free Tier"
        }

@router.get("/analytics")
def get_user_analytics(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    username = current_user.get("username")  # Fixed BOLA vulnerability
    host = db.query(Host).filter(Host.username == username).first()
    
    if not host:
        raise HTTPException(status_code=404, detail="User not found")
        
    sub_tier = "Free Tier"
    if host.subscription and host.subscription.status == "active":
        sub_tier = host.subscription.plan_details or "Pro"
        sub_tier = sub_tier.capitalize()
    else:
        sub_tier = getattr(host, "subscription_tier", "Pro")

    return {
        "subscription_tier": sub_tier,
        "recent_queries": [
            {"query": "What are the STR laws in Miami?", "date": "2026-04-10"},
            {"query": "Do I need a permit for Aspen?", "date": "2026-04-11"},
            {"query": "Is a 30-day minimum stay required in Orlando?", "date": "2026-04-12"}
        ]
    }
