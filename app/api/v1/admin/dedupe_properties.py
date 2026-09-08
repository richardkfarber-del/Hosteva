"""US-018b / TE-010 — Admin-triggered host-scoped duplicate property cleanup."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.duplicate_cleanup import cleanup_all_host_duplicates

router = APIRouter(prefix="/api/v1/admin/properties", tags=["Admin Property Dedupe"])


def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    expected = os.getenv("RESEARCH_ADMIN_KEY") or os.getenv("ADMIN_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin API not configured")
    if not x_admin_key or x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@router.post("/dedupe-duplicates")
def dedupe_duplicate_properties(
    host_id: Optional[str] = Query(
        None, description="Optional host scope; omit to scan all hosts"
    ),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
) -> Dict[str, Any]:
    """Collapse existing same-host address duplicates onto one canonical each.

    Host-scoped only. Idempotent. Uses US-018 matching + richest-then-earliest
    canonical rule (see CHANGELOG / duplicate_cleanup module docstring).
    """
    result = cleanup_all_host_duplicates(db, host_id=host_id)
    return {
        "ok": True,
        "canonical_rule": (
            "richest compliance/checklist state, else earliest created_at, else id"
        ),
        **result.to_dict(),
    }
