"""Auth password lifecycle on /api/v1/users (US-013, US-014)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.password_policy import PasswordPolicyError, validate_password
from app.core.security import get_current_user, get_password_hash, verify_password
from app.database import get_db
from app.models.host import Host
from app.services.email_resend import GENERIC_RESET_OK
from app.services.password_reset import (
    lookup_valid_token,
    mark_token_used,
    request_password_reset,
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class ForgotRequest(BaseModel):
    email: EmailStr


class ResetConfirmRequest(BaseModel):
    token: str = Field(..., min_length=8)
    new_password: str
    confirm_password: str


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


@router.post("/me/password")
def change_password(
    body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    username = current_user.get("username") or current_user.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    if body.new_password != body.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match.")

    host = db.query(Host).filter(Host.username == username).first()
    if not host:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    if not verify_password(body.current_password, host.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    try:
        validate_password(body.new_password)
    except PasswordPolicyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    host.password_hash = get_password_hash(body.new_password)
    db.commit()
    return {"ok": True}


@router.post("/password-reset/request")
def password_reset_request(body: ForgotRequest, request: Request, db: Session = Depends(get_db)):
    request_password_reset(
        db,
        str(body.email),
        requested_ip=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return {"ok": True, "message": GENERIC_RESET_OK}


@router.post("/password-reset/confirm")
def password_reset_confirm(body: ResetConfirmRequest, db: Session = Depends(get_db)):
    if body.new_password != body.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match.")
    try:
        validate_password(body.new_password)
    except PasswordPolicyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    row = lookup_valid_token(db, body.token)
    if row is None:
        raise HTTPException(
            status_code=400,
            detail="This reset link is invalid or has expired. Request a new one.",
        )
    host = db.query(Host).filter(Host.id == row.host_id).first()
    if host is None:
        raise HTTPException(
            status_code=400,
            detail="This reset link is invalid or has expired. Request a new one.",
        )
    host.password_hash = get_password_hash(body.new_password)
    mark_token_used(db, row)
    db.commit()
    return {"ok": True}
