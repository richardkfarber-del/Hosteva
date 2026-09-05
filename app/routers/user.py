import os
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.host import Host
from app.core.security import get_current_user, verify_password, get_password_hash, create_access_token
from app.core.password_policy import validate_password, PasswordPolicyError

router = APIRouter(prefix="/api/user", tags=["User"])

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        validate_password(user_data.password)
    except PasswordPolicyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    email_norm = (user_data.email or "").strip().lower()
    existing_username = db.query(Host).filter(Host.username == user_data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = db.query(Host).filter(Host.email == email_norm).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(user_data.password)
    new_host = Host(
        username=user_data.username,
        email=email_norm,
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
        secure=is_production,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Mirror /api/v1/users/me: never swallow auth/host misses into Guest."""
    import logging
    from app.core.billing_gate import me_entitlement_fields

    username = current_user.get("username") or current_user.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    try:
        host = db.query(Host).filter(Host.username == username).first()
    except Exception:
        logging.exception("api/user/me host lookup failed")
        host = None

    if not host:
        return {
            "username": username,
            "email": "",
            "full_name": username,
            "tier": "Free Tier",
            "has_active_subscription": False,
            "subscription_tier": "FREE",
            "subscription_status": "inactive",
        }

    try:
        ent = me_entitlement_fields(db, host)
    except Exception:
        logging.exception("api/user/me subscription read failed; defaulting Free Tier")
        ent = {
            "tier": "Free Tier",
            "has_active_subscription": False,
            "subscription_tier": "FREE",
            "subscription_status": "inactive",
        }

    return {
        "id": str(host.id) if getattr(host, "id", None) is not None else None,
        "username": host.username,
        "email": getattr(host, "email", "") or "",
        "full_name": host.username,
        **ent,
    }

@router.get("/analytics")
def get_user_analytics(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    username = current_user.get("username")
    host = db.query(Host).filter(Host.username == username).first()

    if not host:
        raise HTTPException(status_code=404, detail="User not found")

    from app.core.billing_gate import me_entitlement_fields
    ent = me_entitlement_fields(db, host)

    is_production = os.getenv("ENVIRONMENT", "").lower() == "production"
    recent_queries = [] if is_production else [
        {"query": "What are the STR laws in Miami?", "date": "2026-04-10"},
        {"query": "Do I need a permit for Aspen?", "date": "2026-04-11"},
        {"query": "Is a 30-day minimum stay required in Orlando?", "date": "2026-04-12"}
    ]
    return {
        "subscription_tier": ent["tier"],
        "has_active_subscription": ent["has_active_subscription"],
        "recent_queries": recent_queries
    }
