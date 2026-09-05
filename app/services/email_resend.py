"""TE-007 — Resend HTTP client for auth transactional mail.

From-address and app base URL come from env only (EMAIL_FROM / RESEND_FROM,
APP_BASE_URL). Do not hardcode sender or product URL here.

EMAIL_SINK=resend|log — production always uses Resend (never /tmp).
"""
from __future__ import annotations

import logging
import os
from typing import Optional

import requests

from app.core.env import is_production

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"
GENERIC_RESET_OK = "If an account exists for that email, we sent reset instructions."


def get_email_from() -> Optional[str]:
    """EMAIL_FROM, falling back to RESEND_FROM. No compiled-in default."""
    value = (os.getenv("EMAIL_FROM") or os.getenv("RESEND_FROM") or "").strip()
    return value or None


def get_app_base_url() -> Optional[str]:
    """APP_BASE_URL from env, no trailing slash. No compiled-in default."""
    value = (os.getenv("APP_BASE_URL") or "").strip().rstrip("/")
    return value or None


def get_email_sink() -> str:
    raw = (os.getenv("EMAIL_SINK") or "").strip().lower()
    if is_production():
        return "resend"
    if raw in ("resend", "log"):
        return raw
    return "log"


def build_reset_url(raw_token: str) -> Optional[str]:
    base = get_app_base_url()
    if not base:
        return None
    return f"{base}/reset-password?token={raw_token}"


def send_password_reset_email(to_email: str, raw_token: str) -> bool:
    """Send reset mail via Resend (or log sink). Never logs token or full URL.

    Returns True if accepted by provider / log sink. Failures are logged for ops
    and return False — callers must not surface provider errors to the client.
    """
    sink = get_email_sink()
    if sink == "log":
        logger.info(
            "EMAIL_SINK=log: password-reset email would be sent (recipient redacted length=%s)",
            len(to_email or ""),
        )
        return True

    from_addr = get_email_from()
    api_key = (os.getenv("RESEND_API_KEY") or "").strip()
    reset_url = build_reset_url(raw_token)
    base = get_app_base_url()

    missing = []
    if not api_key:
        missing.append("RESEND_API_KEY")
    if not from_addr:
        missing.append("EMAIL_FROM/RESEND_FROM")
    if not base:
        missing.append("APP_BASE_URL")
    if is_production() and base and not base.startswith("https://"):
        logger.error("APP_BASE_URL must be https:// in production; reset mail not sent")
        return False
    if missing or not reset_url:
        logger.error(
            "Password-reset mail not sent: missing env %s",
            ",".join(missing) if missing else "APP_BASE_URL",
        )
        return False

    text_body = (
        "Reset your Hosteva password\n\n"
        "Use the link below to choose a new password. "
        "This link expires in 60 minutes and can be used once.\n\n"
        f"{reset_url}\n\n"
        "If you didn't ask for this, ignore this email."
    )
    html_body = (
        "<p>Reset your Hosteva password</p>"
        "<p>Use the button below to choose a new password. "
        "This link expires in 60 minutes and can be used once.</p>"
        f'<p><a href="{reset_url}">Reset password</a></p>'
        "<p>If you didn't ask for this, ignore this email.</p>"
    )

    try:
        resp = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_addr,
                "to": [to_email],
                "subject": "Reset your Hosteva password",
                "html": html_body,
                "text": text_body,
            },
            timeout=15,
        )
    except requests.RequestException:
        logger.exception("Resend request failed (no token logged)")
        return False

    resend_id = None
    try:
        body = resp.json()
        if isinstance(body, dict):
            resend_id = body.get("id")
    except ValueError:
        body = None

    if resp.status_code >= 400:
        logger.error(
            "Resend rejected password-reset send status=%s resend_id=%s",
            resp.status_code,
            resend_id,
        )
        return False

    logger.info(
        "Resend accepted password-reset send status=%s resend_id=%s",
        resp.status_code,
        resend_id,
    )
    return True
