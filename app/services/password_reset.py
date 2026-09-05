"""US-014 token lifecycle: urlsafe raw token, SHA-256 at rest, 60m TTL, single-use."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.host import Host
from app.models.password_reset import PasswordResetToken
from app.services.email_resend import send_password_reset_email

logger = logging.getLogger(__name__)

_RATE_LOCK = Lock()
_EMAIL_HITS: dict[str, list[float]] = defaultdict(list)
_IP_HITS: dict[str, list[float]] = defaultdict(list)
_EMAIL_LIMIT = 5
_IP_LIMIT = 20
_WINDOW_SECONDS = 3600


def reset_ttl_minutes() -> int:
    raw = (os.getenv("PASSWORD_RESET_TTL_MINUTES") or "60").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 60
    return value if value > 0 else 60


def hash_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_raw_token() -> str:
    return secrets.token_urlsafe(32)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _prune(hits: list[float], now: float) -> list[float]:
    cutoff = now - _WINDOW_SECONDS
    return [t for t in hits if t > cutoff]


def is_rate_limited(email: str, ip: Optional[str]) -> bool:
    now = _utcnow().timestamp()
    key = normalize_email(email)
    ip_key = (ip or "").strip() or "unknown"
    with _RATE_LOCK:
        email_hits = _prune(_EMAIL_HITS[key], now)
        ip_hits = _prune(_IP_HITS[ip_key], now)
        _EMAIL_HITS[key] = email_hits
        _IP_HITS[ip_key] = ip_hits
        if len(email_hits) >= _EMAIL_LIMIT or len(ip_hits) >= _IP_LIMIT:
            return True
        email_hits.append(now)
        ip_hits.append(now)
        _EMAIL_HITS[key] = email_hits
        _IP_HITS[ip_key] = ip_hits
        return False


def invalidate_prior_tokens(db: Session, host_id: str) -> None:
    now = _utcnow()
    rows = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.host_id == host_id,
            PasswordResetToken.used_at.is_(None),
        )
        .all()
    )
    for row in rows:
        row.used_at = now


def issue_reset_for_host(
    db: Session,
    host: Host,
    requested_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> str:
    """Invalidate prior unused tokens, persist hashed token, return raw token."""
    invalidate_prior_tokens(db, host.id)
    raw = generate_raw_token()
    row = PasswordResetToken(
        host_id=host.id,
        token_hash=hash_reset_token(raw),
        expires_at=_utcnow() + timedelta(minutes=reset_ttl_minutes()),
        requested_ip=(requested_ip or "")[:200] or None,
        user_agent=(user_agent or "")[:400] or None,
    )
    db.add(row)
    db.commit()
    return raw


def request_password_reset(
    db: Session,
    email: str,
    requested_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Anti-enumeration: always no-op to caller. Send only if host exists."""
    normalized = normalize_email(email)
    if not normalized:
        return
    if is_rate_limited(normalized, requested_ip):
        logger.info("password-reset request rate-limited")
        return
    host = db.query(Host).filter(func.lower(Host.email) == normalized).first()
    if host is None:
        return
    raw = issue_reset_for_host(db, host, requested_ip=requested_ip, user_agent=user_agent)
    sent = send_password_reset_email(host.email, raw)
    if not sent:
        logger.error("password-reset email delivery failed for existing host (no token logged)")


def lookup_valid_token(db: Session, raw_token: str) -> Optional[PasswordResetToken]:
    if not raw_token or not isinstance(raw_token, str):
        return None
    digest = hash_reset_token(raw_token)
    row = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == digest,
            PasswordResetToken.used_at.is_(None),
        )
        .first()
    )
    if row is None:
        return None
    expires = _as_aware(row.expires_at)
    if expires is None or expires <= _utcnow():
        return None
    return row


def mark_token_used(db: Session, row: PasswordResetToken) -> None:
    now = _utcnow()
    row.used_at = now
    others = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.host_id == row.host_id,
            PasswordResetToken.id != row.id,
            PasswordResetToken.used_at.is_(None),
        )
        .all()
    )
    for other in others:
        other.used_at = now
