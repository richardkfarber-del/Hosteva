"""SP-011: enqueue internal research on Free Audit miss — draft only, never Covered."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.research_request import ResearchRequest

logger = logging.getLogger(__name__)

ACTIVE_STATUSES = ("queued", "in_progress", "draft_ready")


def jurisdiction_key(state: str, municipality: str, jurisdiction_type: Optional[str] = None) -> str:
    st = (state or "").strip().lower()
    muni = (municipality or "").strip().lower() or "*"
    jt = (jurisdiction_type or "city").strip().lower()
    return f"{st}|{muni}|{jt}"


def truncate_address(address: Optional[str], max_len: int = 120) -> Optional[str]:
    if not address:
        return None
    a = address.strip()
    if len(a) <= max_len:
        return a
    return a[: max_len - 1] + "…"


def enqueue_research(
    db: Session,
    *,
    state: str,
    municipality_name: str,
    jurisdiction_type: Optional[str] = "city",
    sample_address: Optional[str] = None,
    host_id: Optional[str] = None,
    trigger_reason: str = "MISSING_MUNICIPAL_CODE",
) -> Optional[ResearchRequest]:
    """
    Idempotent enqueue by jurisdiction_key.
    Never flips Covered / is_expert_verified. No scrape on hot path.
    """
    if not state or not municipality_name:
        return None

    key = jurisdiction_key(state, municipality_name, jurisdiction_type)
    existing = (
        db.query(ResearchRequest)
        .filter(ResearchRequest.jurisdiction_key == key)
        .first()
    )

    if existing:
        if existing.status in ACTIVE_STATUSES:
            existing.hit_count = (existing.hit_count or 1) + 1
            if sample_address:
                existing.sample_address = truncate_address(sample_address)
            existing.updated_at = datetime.now(timezone.utc)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            logger.info("research_enqueue dedupe key=%s hits=%s", key, existing.hit_count)
            return existing
        if existing.status == "promoted":
            # Do not re-queue promoted unless Thin refresh (handled by caller reason)
            if trigger_reason != "THIN_REFRESH":
                return existing
        # rejected or promoted+refresh → reopen as queued
        existing.status = "queued"
        existing.trigger_reason = trigger_reason
        existing.hit_count = (existing.hit_count or 0) + 1
        existing.sample_address = truncate_address(sample_address) or existing.sample_address
        existing.draft_payload = None
        existing.completed_at = None
        existing.updated_at = datetime.now(timezone.utc)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        logger.info("research_enqueue reopen key=%s", key)
        return existing

    row = ResearchRequest(
        jurisdiction_key=key,
        state=(state or "").strip().upper()[:10],
        municipality_name=(municipality_name or "").strip()[:150],
        jurisdiction_type=(jurisdiction_type or "city"),
        sample_address=truncate_address(sample_address),
        host_id=host_id,
        status="queued",
        trigger_reason=trigger_reason,
        priority=100,
        hit_count=1,
        draft_payload=None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    logger.info("research_enqueue created key=%s id=%s", key, row.id)
    return row


def claim_and_draft_stub(db: Session, request_id) -> Optional[ResearchRequest]:
    """
    Cheap worker: mark draft_ready with empty non-authoritative payload.
    Does NOT insert MunicipalCode / does NOT set is_expert_verified.
    """
    row = db.query(ResearchRequest).filter(ResearchRequest.id == request_id).first()
    if not row or row.status not in ("queued", "in_progress"):
        return row
    row.status = "in_progress"
    db.add(row)
    db.commit()

    payload = {
        "source_kind": "ai_draft",
        "candidate_source_urls": [],
        "str_permitted_raw": None,
        "requires_permit": None,
        "tax_notes": None,
        "checklist_candidates": [],
        "model_or_fetch": "stub",
        "confidence": "low",
        "note": "Human curation required before Covered. Not authoritative.",
    }
    row.draft_payload = json.dumps(payload)
    row.status = "draft_ready"
    row.worker_notes = "Stub draft only — no scrape; awaiting human promote."
    row.updated_at = datetime.now(timezone.utc)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
