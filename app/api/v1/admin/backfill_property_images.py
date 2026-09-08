"""BUG-PL-08 — Admin-triggered property image backfill into object storage."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.property_image_heal import backfill_property_images

router = APIRouter(prefix="/api/v1/admin/properties", tags=["Admin Property Images"])


def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    expected = os.getenv("RESEARCH_ADMIN_KEY") or os.getenv("ADMIN_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin API not configured")
    if not x_admin_key or x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@router.post("/backfill-images")
def backfill_images(
    host_id: Optional[str] = Query(
        None, description="Optional host scope; omit to scan all hosts"
    ),
    limit: Optional[int] = Query(
        None, description="Optional max rows to scan (for staged rollout)"
    ),
    verify_remote: bool = Query(
        True,
        description="HEAD-check existing HTTPS image URLs (default true for backfill)",
    ),
    include_placeholders: Optional[bool] = Query(
        None,
        description=(
            "Retry fallback_house.jpg / empty rows (SV re-fetch → upload). "
            "Default: true when PROPERTY_IMAGE_* storage is configured, else false."
        ),
    ),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
) -> Dict[str, Any]:
    """Rehydrate ephemeral `/static/property_images/*` (and broken HTTPS) via C→B.

    When storage is configured, also retries placeholder rows so fail-closed
    images can recover after R2/credentials are fixed.
    Uploads to PROPERTY_IMAGE_* object storage and rewrites image_url.
    Fail-closed to fallback_house.jpg + placeholder honesty when Maps fails.
    Idempotent for already-durable healthy URLs.
    """
    result = backfill_property_images(
        db,
        host_id=host_id,
        limit=limit,
        verify_remote=verify_remote,
        include_placeholders=include_placeholders,
    )
    return {
        "ok": True,
        "provider_hint": "Cloudflare R2 (default) or AWS S3 via PROPERTY_IMAGE_PROVIDER",
        **result.to_dict(),
    }
