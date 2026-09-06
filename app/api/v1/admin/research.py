"""SP-011 admin research queue API — staff/admin key only."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.research_request import ResearchRequest
from app.models.compliance import MunicipalCode
from app.services.research_queue import claim_and_draft_stub

router = APIRouter(prefix="/api/v1/admin/research-requests", tags=["Admin Research Queue"])


def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    expected = os.getenv("RESEARCH_ADMIN_KEY") or os.getenv("ADMIN_API_KEY")
    if not expected:
        # Fail closed when unset — do not expose queue publicly
        raise HTTPException(status_code=503, detail="Admin research API not configured")
    if not x_admin_key or x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


class ResearchRequestOut(BaseModel):
    id: str
    jurisdiction_key: str
    state: str
    municipality_name: str
    jurisdiction_type: Optional[str] = None
    sample_address: Optional[str] = None
    status: str
    trigger_reason: Optional[str] = None
    priority: int
    hit_count: int
    draft_payload: Optional[str] = None
    worker_notes: Optional[str] = None

    class Config:
        from_attributes = True


class PromoteBody(BaseModel):
    source_url: str = Field(..., min_length=4)
    str_permitted_raw: Optional[str] = "Yes"
    requires_permit: bool = True
    is_allowed: bool = True
    str_prohibited: bool = False
    permit_name: Optional[str] = None
    tax_rate: Optional[float] = None
    jurisdiction_type: Optional[str] = None


class RejectBody(BaseModel):
    reason: str = Field(..., min_length=1)


@router.get("", response_model=List[ResearchRequestOut])
def list_research_requests(
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    q = db.query(ResearchRequest).order_by(ResearchRequest.updated_at.desc())
    if status:
        q = q.filter(ResearchRequest.status == status)
    rows = q.limit(limit).all()
    return [
        ResearchRequestOut(
            id=str(r.id),
            jurisdiction_key=r.jurisdiction_key,
            state=r.state,
            municipality_name=r.municipality_name,
            jurisdiction_type=r.jurisdiction_type,
            sample_address=r.sample_address,
            status=r.status,
            trigger_reason=r.trigger_reason,
            priority=r.priority or 100,
            hit_count=r.hit_count or 1,
            draft_payload=r.draft_payload,
            worker_notes=r.worker_notes,
        )
        for r in rows
    ]


@router.get("/{request_id}", response_model=ResearchRequestOut)
def get_research_request(
    request_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    row = db.query(ResearchRequest).filter(ResearchRequest.id == request_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return ResearchRequestOut(
        id=str(row.id),
        jurisdiction_key=row.jurisdiction_key,
        state=row.state,
        municipality_name=row.municipality_name,
        jurisdiction_type=row.jurisdiction_type,
        sample_address=row.sample_address,
        status=row.status,
        trigger_reason=row.trigger_reason,
        priority=row.priority or 100,
        hit_count=row.hit_count or 1,
        draft_payload=row.draft_payload,
        worker_notes=row.worker_notes,
    )


@router.post("/{request_id}/draft-stub", response_model=ResearchRequestOut)
def run_draft_stub(
    request_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    """Optional: move queued → draft_ready with non-authoritative stub payload."""
    row = claim_and_draft_stub(db, request_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return get_research_request(request_id, db, True)


@router.post("/{request_id}/promote")
def promote_research_request(
    request_id: str,
    body: PromoteBody,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    """Human promote only path to Curated MunicipalCode."""
    row = db.query(ResearchRequest).filter(ResearchRequest.id == request_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    if not body.source_url or "." not in body.source_url:
        raise HTTPException(status_code=400, detail="source_url required for promote")

    jt = body.jurisdiction_type or row.jurisdiction_type or "City"
    existing = (
        db.query(MunicipalCode)
        .filter(
            MunicipalCode.municipality_name.ilike(row.municipality_name),
            MunicipalCode.state.ilike(row.state),
        )
        .first()
    )
    today = datetime.now(timezone.utc).date()
    if existing:
        existing.is_expert_verified = True
        existing.is_ai_scraped = False
        existing.source_url = body.source_url
        existing.str_permitted_raw = body.str_permitted_raw
        existing.requires_permit = body.requires_permit
        existing.is_allowed = body.is_allowed
        existing.str_prohibited = body.str_prohibited
        existing.permit_name = body.permit_name
        existing.tax_rate = body.tax_rate
        existing.last_verified_date = today
        existing.jurisdiction_type = jt
        if hasattr(existing, "source_kind"):
            existing.source_kind = "manual_pack"
        mc = existing
    else:
        mc = MunicipalCode(
            municipality_name=row.municipality_name,
            jurisdiction_type=jt,
            state=row.state.upper(),
            ordinance_number="CURATED-PROMOTE",
            str_prohibited=body.str_prohibited,
            is_allowed=body.is_allowed,
            requires_permit=body.requires_permit,
            permit_name=body.permit_name,
            tax_rate=body.tax_rate,
            source_url=body.source_url,
            str_permitted_raw=body.str_permitted_raw,
            last_verified_date=today,
            is_ai_scraped=False,
            is_expert_verified=True,
        )
        if hasattr(mc, "source_kind"):
            mc.source_kind = "manual_pack"
        db.add(mc)

    row.status = "promoted"
    row.completed_at = datetime.now(timezone.utc)
    row.draft_municipal_code_id = mc.id
    row.worker_notes = (row.worker_notes or "") + "\nPromoted by admin."
    db.add(row)
    db.commit()
    return {"status": "promoted", "municipal_code_id": str(mc.id), "request_id": str(row.id)}


@router.post("/{request_id}/reject")
def reject_research_request(
    request_id: str,
    body: RejectBody,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    row = db.query(ResearchRequest).filter(ResearchRequest.id == request_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    row.status = "rejected"
    row.completed_at = datetime.now(timezone.utc)
    row.worker_notes = body.reason
    db.add(row)
    db.commit()
    return {"status": "rejected", "request_id": str(row.id)}
