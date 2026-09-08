"""US-018b / TE-010 — Host-scoped cleanup of existing duplicate properties.

Reuses US-018 matching from ``duplicate_address.addresses_equivalent``.
Never merges or deletes across hosts.

Canonical rule (documented in CHANGELOG):
  1. Prefer the property with the richest compliance/checklist state
     (more checklist rows, compliant flags, advanced statuses, uploads,
     image_url, non-Pending zoning, iCal links).
  2. Tie-break: earliest ``created_at`` (nulls last), then lexicographic ``id``.

Children (property_compliance, permit_transactions, reservations,
guest_messages, property_listings, compliance_reports) are reattached to
the canonical when possible; on unique-key conflict the richer / existing
canonical row is kept and the duplicate child is discarded.
Non-canonical property rows are hard-deleted (CASCADE cleans any leftovers)
so they disappear from the host dashboard.
Idempotent: a second run finds no duplicate clusters and is a no-op.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy.orm import Session

from app.models.property import Property
from app.models.compliance import PropertyCompliance
from app.models.oauth import PropertyListing
from app.models.zoning import ComplianceReport
from app.db_models import PermitTransaction, Reservation, GuestMessage
from app.services.duplicate_address import addresses_equivalent

logger = logging.getLogger(__name__)

# Higher = richer checklist progress
_STATUS_RANK = {
    "VERIFIED": 6,
    "APPROVED": 6,
    "COMPLIANT": 6,
    "COMPLETED": 5,
    "COMPLETE": 5,
    "UPLOADED": 4,
    "IN_REVIEW": 3,
    "PENDING_REVIEW": 3,
    "PENDING": 1,
    "REJECTED": 0,
    "FAILED": 0,
}


@dataclass
class MergeGroupResult:
    host_id: str
    canonical_id: str
    removed_ids: List[str]
    children_moved: int = 0
    children_discarded: int = 0


@dataclass
class CleanupResult:
    hosts_scanned: int = 0
    groups_merged: int = 0
    properties_removed: int = 0
    children_moved: int = 0
    children_discarded: int = 0
    groups: List[MergeGroupResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hosts_scanned": self.hosts_scanned,
            "groups_merged": self.groups_merged,
            "properties_removed": self.properties_removed,
            "children_moved": self.children_moved,
            "children_discarded": self.children_discarded,
            "groups": [
                {
                    "host_id": g.host_id,
                    "canonical_id": g.canonical_id,
                    "removed_ids": g.removed_ids,
                    "children_moved": g.children_moved,
                    "children_discarded": g.children_discarded,
                }
                for g in self.groups
            ],
        }


def _status_rank(status: Optional[str]) -> int:
    if not status:
        return 0
    return _STATUS_RANK.get(str(status).strip().upper(), 1)


def _created_at_key(prop: Property) -> datetime:
    ts = prop.created_at
    if ts is None:
        return datetime.max.replace(tzinfo=timezone.utc)
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts


def compliance_richness_score(db: Session, prop: Property) -> int:
    """Numeric richness of compliance/checklist (+ light property metadata)."""
    items = (
        db.query(PropertyCompliance)
        .filter(PropertyCompliance.property_id == prop.id)
        .all()
    )
    score = 0
    score += len(items) * 10
    for item in items:
        if item.is_compliant:
            score += 5
        score += _status_rank(item.status)
        if item.uploaded_file_url:
            score += 3
        if item.ocr_metadata_json:
            score += 1
        if item.verification_notes:
            score += 1
    if prop.image_url:
        score += 2
    zoning = (prop.zoning_status or "").strip()
    if zoning and zoning.casefold() not in ("pending", ""):
        score += 2
    if prop.required_permits:
        score += 1
    if prop.local_restrictions:
        score += 1
    if prop.airbnb_ical_import_url or prop.vrbo_ical_import_url:
        score += 1
    # Paid / entitlement-adjacent permit txs count as richness
    permit_n = (
        db.query(PermitTransaction)
        .filter(PermitTransaction.property_id == prop.id)
        .count()
    )
    score += permit_n * 4
    return score


def select_canonical(db: Session, props: Sequence[Property]) -> Property:
    """Deterministic canonical: richest score, else earliest created_at, else id."""
    if not props:
        raise ValueError("select_canonical requires at least one property")

    def sort_key(p: Property) -> Tuple[int, datetime, str]:
        # Negate score so higher richness sorts first with ascending key… use reverse
        return (-compliance_richness_score(db, p), _created_at_key(p), p.id or "")

    return sorted(props, key=sort_key)[0]


def _cluster_host_duplicates(props: Sequence[Property]) -> List[List[Property]]:
    """Union-find clusters of address-equivalent properties within one host."""
    n = len(props)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        pi, pj = find(i), find(j)
        if pi != pj:
            parent[pi] = pj

    for i in range(n):
        for j in range(i + 1, n):
            a, b = props[i], props[j]
            if addresses_equivalent(
                a.address,
                a.city,
                a.state,
                a.zip_code or "",
                b.address,
                b.city,
                b.state,
                b.zip_code or "",
            ):
                union(i, j)

    buckets: Dict[int, List[Property]] = {}
    for i, prop in enumerate(props):
        buckets.setdefault(find(i), []).append(prop)
    return list(buckets.values())


def _item_richness(item: PropertyCompliance) -> int:
    score = _status_rank(item.status)
    if item.is_compliant:
        score += 5
    if item.uploaded_file_url:
        score += 3
    if item.ocr_metadata_json:
        score += 1
    if item.verification_notes:
        score += 1
    return score


def _merge_scalar_fields(canonical: Property, donor: Property) -> None:
    """Fill blank canonical fields from donor (preserve richest scalars)."""
    if not canonical.image_url and donor.image_url:
        canonical.image_url = donor.image_url
    if (not canonical.zoning_status or canonical.zoning_status.casefold() == "pending") and (
        donor.zoning_status and donor.zoning_status.casefold() != "pending"
    ):
        canonical.zoning_status = donor.zoning_status
    if not canonical.required_permits and donor.required_permits:
        canonical.required_permits = donor.required_permits
    if not canonical.local_restrictions and donor.local_restrictions:
        canonical.local_restrictions = donor.local_restrictions
    if not canonical.property_type and donor.property_type:
        canonical.property_type = donor.property_type
    if not canonical.zip_code and donor.zip_code:
        canonical.zip_code = donor.zip_code
    if not canonical.airbnb_ical_import_url and donor.airbnb_ical_import_url:
        canonical.airbnb_ical_import_url = donor.airbnb_ical_import_url
    if not canonical.vrbo_ical_import_url and donor.vrbo_ical_import_url:
        canonical.vrbo_ical_import_url = donor.vrbo_ical_import_url
    # Keep canonical export token; only adopt donor's if canonical lacks one
    if not canonical.hosteva_ical_export_token and donor.hosteva_ical_export_token:
        canonical.hosteva_ical_export_token = donor.hosteva_ical_export_token
        donor.hosteva_ical_export_token = None  # avoid unique clash on delete path


def _reattach_compliance(
    db: Session, canonical_id: str, donor_id: str
) -> Tuple[int, int]:
    moved = discarded = 0
    donor_items = (
        db.query(PropertyCompliance)
        .filter(PropertyCompliance.property_id == donor_id)
        .all()
    )
    canon_items = (
        db.query(PropertyCompliance)
        .filter(PropertyCompliance.property_id == canonical_id)
        .all()
    )

    def conflict_key(item: PropertyCompliance) -> Tuple[Any, str]:
        name = (item.task_name or "").strip().casefold()
        return (item.municipal_code_id, name)

    canon_by_key: Dict[Tuple[Any, str], PropertyCompliance] = {}
    for item in canon_items:
        key = conflict_key(item)
        existing = canon_by_key.get(key)
        if existing is None or _item_richness(item) > _item_richness(existing):
            canon_by_key[key] = item

    for item in donor_items:
        key = conflict_key(item)
        existing = canon_by_key.get(key)
        if existing is None:
            item.property_id = canonical_id
            canon_by_key[key] = item
            moved += 1
        elif _item_richness(item) > _item_richness(existing):
            # Prefer donor's richer row: move donor, drop weaker canonical twin
            db.delete(existing)
            item.property_id = canonical_id
            canon_by_key[key] = item
            moved += 1
            discarded += 1
        else:
            db.delete(item)
            discarded += 1
    return moved, discarded



def _reattach_listings(
    db: Session, canonical_id: str, donor_id: str
) -> Tuple[int, int]:
    moved = discarded = 0
    donor_rows = (
        db.query(PropertyListing).filter(PropertyListing.property_id == donor_id).all()
    )
    canon_platforms = {
        r.platform_name
        for r in db.query(PropertyListing)
        .filter(PropertyListing.property_id == canonical_id)
        .all()
    }
    for row in donor_rows:
        if row.platform_name in canon_platforms:
            db.delete(row)
            discarded += 1
        else:
            row.property_id = canonical_id
            canon_platforms.add(row.platform_name)
            moved += 1
    return moved, discarded


def _reattach_reports(db: Session, canonical_id: str, donor_id: str) -> Tuple[int, int]:
    moved = 0
    rows = (
        db.query(ComplianceReport)
        .filter(ComplianceReport.property_id == donor_id)
        .all()
    )
    for row in rows:
        row.property_id = canonical_id
        moved += 1
    return moved, 0


def _reattach_permits_reservations_messages(
    db: Session, canonical_id: str, donor_id: str
) -> Tuple[int, int]:
    moved = discarded = 0
    for model in (PermitTransaction, Reservation, GuestMessage):
        rows = db.query(model).filter(model.property_id == donor_id).all()
        for row in rows:
            row.property_id = canonical_id
            moved += 1
    return moved, discarded


def merge_duplicate_group(
    db: Session, host_id: str, props: Sequence[Property]
) -> MergeGroupResult:
    """Collapse one host-scoped duplicate cluster onto a single canonical."""
    if len(props) < 2:
        raise ValueError("merge_duplicate_group requires 2+ properties")
    if any(p.user_id != host_id for p in props):
        raise ValueError("Cross-host merge refused — all props must belong to host_id")

    canonical = select_canonical(db, props)
    removed = [p for p in props if p.id != canonical.id]
    children_moved = children_discarded = 0

    for donor in removed:
        _merge_scalar_fields(canonical, donor)
        m, d = _reattach_compliance(db, canonical.id, donor.id)
        children_moved += m
        children_discarded += d
        m, d = _reattach_listings(db, canonical.id, donor.id)
        children_moved += m
        children_discarded += d
        m, d = _reattach_reports(db, canonical.id, donor.id)
        children_moved += m
        children_discarded += d
        m, d = _reattach_permits_reservations_messages(db, canonical.id, donor.id)
        children_moved += m
        children_discarded += d
        db.delete(donor)

    db.flush()
    return MergeGroupResult(
        host_id=host_id,
        canonical_id=canonical.id,
        removed_ids=[p.id for p in removed],
        children_moved=children_moved,
        children_discarded=children_discarded,
    )


def cleanup_host_duplicates(db: Session, host_id: str) -> CleanupResult:
    """Dedupe one host. Host-scoped only."""
    result = CleanupResult(hosts_scanned=1)
    props = db.query(Property).filter(Property.user_id == host_id).all()
    clusters = _cluster_host_duplicates(props)
    for cluster in clusters:
        if len(cluster) < 2:
            continue
        group = merge_duplicate_group(db, host_id, cluster)
        result.groups.append(group)
        result.groups_merged += 1
        result.properties_removed += len(group.removed_ids)
        result.children_moved += group.children_moved
        result.children_discarded += group.children_discarded
    return result


def cleanup_all_host_duplicates(
    db: Session, host_id: Optional[str] = None
) -> CleanupResult:
    """Run cleanup for one host or every distinct property owner.

    Never crosses hosts. Idempotent.
    """
    if host_id:
        result = cleanup_host_duplicates(db, host_id)
        db.commit()
        return result

    host_ids = [
        row[0]
        for row in db.query(Property.user_id)
        .filter(Property.user_id.isnot(None))
        .distinct()
        .all()
    ]
    aggregate = CleanupResult()
    for hid in host_ids:
        partial = cleanup_host_duplicates(db, hid)
        aggregate.hosts_scanned += partial.hosts_scanned
        aggregate.groups_merged += partial.groups_merged
        aggregate.properties_removed += partial.properties_removed
        aggregate.children_moved += partial.children_moved
        aggregate.children_discarded += partial.children_discarded
        aggregate.groups.extend(partial.groups)
    db.commit()
    logger.info(
        "US-018b cleanup done hosts=%s groups=%s removed=%s",
        aggregate.hosts_scanned,
        aggregate.groups_merged,
        aggregate.properties_removed,
    )
    return aggregate
