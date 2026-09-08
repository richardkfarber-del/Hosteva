from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import os
import uuid
from sqlalchemy.orm import Session
from app.models.property import Property
from app.services.florida_compliance_engine import FloridaComplianceEngine


class PermitNotApplicableError(ValueError):
    """Raised when permit generation is not applicable for this property/jurisdiction."""


class PermitGeneratorService:
    """
    Service for generating automated permit applications based on property compliance data.
    Leverages FloridaComplianceEngine to determine requirements and generate applications.
    """

    UNDER_REVIEW_LABELS = {
        "under review",
        "under_review",
        "pending",
        "awaiting audit",
        "thin",
    }

    @staticmethod
    def _attr_int(property_obj, *names: str, default: int = 0) -> int:
        """Read the first present numeric attribute (supports beds vs bedrooms mismatch)."""
        for name in names:
            if hasattr(property_obj, name):
                val = getattr(property_obj, name)
                if val is None:
                    continue
                try:
                    return int(val)
                except (TypeError, ValueError):
                    continue
        return default

    @staticmethod
    def _attr_bool(property_obj, *names: str, default: bool = False) -> bool:
        for name in names:
            if hasattr(property_obj, name):
                val = getattr(property_obj, name)
                if val is None:
                    continue
                return bool(val)
        return default

    @staticmethod
    def _bed_count(property_obj) -> int:
        """Property API exposes beds; older code expected bedrooms. Prefer beds."""
        return PermitGeneratorService._attr_int(
            property_obj, "beds", "bedrooms", "num_bedrooms", default=2
        )

    @staticmethod
    def _parse_json_field(raw) -> Any:
        if raw is None or raw == "":
            return None
        if isinstance(raw, (list, dict)):
            return raw
        try:
            return json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None

    @staticmethod
    def permit_applicability(property_obj: Property) -> Tuple[bool, Optional[str]]:
        """
        Return (applicable, reason_if_not).
        Under Review / research-pending and no-permit jurisdictions → N/A.
        """
        zs = (getattr(property_obj, "zoning_status", None) or "").strip().lower()
        if zs in PermitGeneratorService.UNDER_REVIEW_LABELS or "under review" in zs:
            return (
                False,
                "Permit generation is not available while this property's jurisdiction "
                "is Under Review / Pending. Hosteva will enable PERMIT once municipal "
                "rules are confirmed.",
            )

        required = PermitGeneratorService._parse_json_field(
            getattr(property_obj, "required_permits", None)
        )
        restrictions = PermitGeneratorService._parse_json_field(
            getattr(property_obj, "local_restrictions", None)
        ) or {}

        requires_permit_flag = restrictions.get("requires_permit")
        if requires_permit_flag is False:
            return (
                False,
                "No short-term rental permit is required for this jurisdiction "
                "(PERMIT is not applicable).",
            )

        # Empty required_permits + explicit no-permit note → N/A
        if isinstance(required, list) and len(required) == 0:
            no_permit_hint = str(
                restrictions.get("permit_status")
                or restrictions.get("disclaimer")
                or restrictions.get("reason")
                or ""
            ).lower()
            if any(
                token in no_permit_hint
                for token in ("no permit", "permit not required", "not required", "n/a")
            ):
                return (
                    False,
                    "No short-term rental permit is required for this jurisdiction "
                    "(PERMIT is not applicable).",
                )

        return True, None

    @staticmethod
    def _write_draft_application(application: Dict[str, Any]) -> Optional[str]:
        """Persist a simple HTML draft so the UI can open a real URL (not #)."""
        try:
            static_gen_dir = os.path.join("app", "static", "generated_permits")
            os.makedirs(static_gen_dir, exist_ok=True)
            filename = f"{application['application_id']}.html"
            path = os.path.join(static_gen_dir, filename)
            docs = "".join(f"<li>{d}</li>" for d in application.get("required_documents", []))
            steps = "".join(f"<li>{s}</li>" for s in application.get("next_steps", []))
            issues = application.get("compliance_summary", {}).get("issues") or []
            issue_items = "".join(
                f"<li>{(i.get('message') or i.get('description') or i)}</li>"
                if isinstance(i, dict)
                else f"<li>{i}</li>"
                for i in issues
            )
            html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>Permit draft {application['application_id']}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:720px;margin:2rem auto;padding:0 1rem;color:#0f172a}}
h1{{font-size:1.4rem}} .meta{{color:#64748b;font-size:.9rem}}
</style></head><body>
<h1>Short-Term Rental Permit Application (Draft)</h1>
<p class="meta">Application ID: {application['application_id']} · County: {application['county']} ·
Generated: {application['generated_at']} · Status: {application['status']}</p>
<p>Property ID: {application['property_id']}</p>
<p>Estimated processing: {application['estimated_processing_time']}</p>
<h2>Required documents</h2><ul>{docs}</ul>
<h2>Next steps</h2><ul>{steps}</ul>
<h2>Compliance notes</h2>
<p>Compliant: {application.get('compliance_summary', {}).get('is_compliant')}</p>
<ul>{issue_items or '<li>None listed</li>'}</ul>
<p class="meta">Draft generated by Hosteva. Not a filed county application. Not legal advice.</p>
</body></html>
"""
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            return f"/static/generated_permits/{filename}"
        except OSError:
            return None

    @staticmethod
    def generate_application(db: Session, property_id: str) -> Dict[str, Any]:
        """
        Generate a permit application for a given property.

        Uses real property attributes (`beds` preferred over legacy `bedrooms`).
        Raises PermitNotApplicableError when PERMIT is N/A.
        """
        property_obj = db.query(Property).filter(Property.id == property_id).first()

        if not property_obj:
            raise ValueError(f"Property with id {property_id} not found")

        applicable, reason = PermitGeneratorService.permit_applicability(property_obj)
        if not applicable:
            raise PermitNotApplicableError(reason or "Permit generation is not applicable.")

        beds = PermitGeneratorService._bed_count(property_obj)
        max_occ = PermitGeneratorService._attr_int(
            property_obj, "max_occupancy", "num_guests", default=max(beds * 2, 4)
        )
        parking = PermitGeneratorService._attr_int(
            property_obj, "parking_spaces", default=1
        )
        has_pool = PermitGeneratorService._attr_bool(
            property_obj, "has_pool", default=False
        )

        # FloridaComplianceEngine expects num_bedrooms / num_guests / parking_spaces
        property_details = {
            "address": property_obj.address,
            "beds": beds,
            "bedrooms": beds,
            "num_bedrooms": beds,
            "max_occupancy": max_occ,
            "num_guests": max_occ,
            "has_pool": has_pool,
            "parking_spaces": parking,
            "has_permit": False,
            "has_fire_safety": True,
        }

        county = PermitGeneratorService._extract_county(
            " ".join(
                part
                for part in [
                    getattr(property_obj, "address", None) or "",
                    getattr(property_obj, "city", None) or "",
                    getattr(property_obj, "state", None) or "",
                ]
                if part
            )
        )

        compliance_result = FloridaComplianceEngine.evaluate_compliance(
            county=county,
            property_details=property_details,
        )

        application_id = f"APP-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"

        required_documents = PermitGeneratorService._get_required_documents(
            county,
            compliance_result,
        )

        next_steps = PermitGeneratorService._generate_next_steps(
            compliance_result.get("is_compliant", False)
        )

        application = {
            "application_id": application_id,
            "property_id": property_id,
            "county": county,
            "application_type": "Short-Term Rental Permit",
            "status": "draft",
            "generated_at": datetime.now(),
            "required_documents": required_documents,
            "compliance_summary": {
                "is_compliant": compliance_result.get("is_compliant", False),
                "issues": compliance_result.get("issues", []),
            },
            "estimated_processing_time": PermitGeneratorService._get_processing_time(county),
            "next_steps": next_steps,
            "beds_used": beds,
        }

        download_url = PermitGeneratorService._write_draft_application(application)
        if download_url:
            application["download_url"] = download_url
            application["application_url"] = download_url

        restrictions = PermitGeneratorService._parse_json_field(
            getattr(property_obj, "local_restrictions", None)
        ) or {}
        external = (
            restrictions.get("permit_application_url")
            or restrictions.get("permit_link")
            or restrictions.get("source_url")
        )
        if external and not application.get("application_url"):
            application["application_url"] = external

        return application

    @staticmethod
    def _extract_county(address: str) -> str:
        """Extract county from address string."""
        address_lower = (address or "").lower()
        if "pasco" in address_lower or "spring hill" in address_lower or "hudson" in address_lower:
            return "Pasco"
        if "hillsborough" in address_lower or "tampa" in address_lower:
            return "Hillsborough"
        return "Pasco"

    @staticmethod
    def _get_required_documents(county: str, compliance_result: Dict) -> List[str]:
        """Determine required documents based on county and compliance status."""
        base_documents = [
            "Form HR-7020 (Florida Short-Term Rental Registration)",
            "Proof of Property Insurance",
            "Fire Safety Inspection Certificate",
            "Smoke Detector Compliance Affidavit",
        ]

        if county == "Pasco":
            base_documents.extend([
                "Pasco County Business Tax Receipt",
                "Floor Plan with Emergency Exits Marked",
            ])
        elif county == "Hillsborough":
            base_documents.extend([
                "Hillsborough County Occupational License",
                "Parking Plan Diagram",
            ])

        issues = compliance_result.get("issues", [])
        for issue in issues:
            text = ""
            if isinstance(issue, dict):
                text = (issue.get("description") or issue.get("message") or "").lower()
            else:
                text = str(issue).lower()
            if "pool" in text:
                base_documents.append("Pool Safety Barrier Certification")
            if "parking" in text:
                base_documents.append("Off-Street Parking Agreement")

        return base_documents

    @staticmethod
    def _get_processing_time(county: str) -> str:
        """Get estimated processing time by county."""
        processing_times = {
            "Pasco": "14-21 business days",
            "Hillsborough": "10-15 business days",
        }
        return processing_times.get(county, "14-21 business days")

    @staticmethod
    def _generate_next_steps(is_compliant: bool) -> List[str]:
        """Generate next steps based on compliance status."""
        if is_compliant:
            return [
                "Review the generated application details",
                "Gather and upload all required documents",
                "Pay applicable permit fees",
                "Submit application to county office",
                "Schedule required inspections",
            ]
        return [
            "Review compliance issues listed above",
            "Address all non-compliant items",
            "Re-run compliance check",
            "Once compliant, proceed with application submission",
        ]
