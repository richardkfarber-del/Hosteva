from sqlalchemy.orm import Session
from app.models.zoning import ZoningRegulation, LandUseType, ZoningDistrict, ComplianceRuleType, ComplianceReport
from app.schemas.zoning import ComplianceCheckRequest
import uuid
import json

class ComplianceEngine:
    @staticmethod
    def evaluate(db: Session, request: ComplianceCheckRequest) -> ComplianceReport:
        # 1. Fetch relevant regulations for this district and land use
        regulations = db.query(ZoningRegulation).filter(
            ZoningRegulation.zoning_district_id == request.zoning_district_id,
            ZoningRegulation.land_use_type_id == request.proposed_land_use_id
        ).all()

        is_compliant = True
        issues = []

        # Map rule type IDs to codes for easy lookup if needed (though we'll use IDs from DB)
        rule_types = {rt.id: rt for rt in db.query(ComplianceRuleType).all()}
        rule_types_by_code = {rt.code: rt for rt in rule_types.values()}

        # 2. Check each regulation
        # Request.actual_values is Dict[rule_type_code, actual_value]
        # We need to match regulation's rule_type_id to the code in actual_values
        
        # Track which required rules are present
        regulated_rule_ids = set()

        for reg in regulations:
            rule_type = rule_types.get(reg.rule_type_id)
            if not rule_type:
                continue
            
            regulated_rule_ids.add(reg.rule_type_id)
            actual_val = request.actual_values.get(rule_type.code)

            # Check if permitted
            if not reg.is_permitted:
                is_compliant = False
                issues.append({
                    "rule_type": rule_type.code,
                    "issue": "Not permitted",
                    "details": f"Proposed land use is not permitted for the specified rule in this district."
                })
                continue

            # Evaluate numeric values
            if actual_val is not None:
                if reg.min_value is not None and actual_val < float(reg.min_value):
                    is_compliant = False
                    issues.append({
                        "rule_type": rule_type.code,
                        "issue": "Below minimum",
                        "expected": float(reg.min_value),
                        "actual": actual_val
                    })
                
                if reg.max_value is not None and actual_val > float(reg.max_value):
                    is_compliant = False
                    issues.append({
                        "rule_type": rule_type.code,
                        "issue": "Above maximum",
                        "expected": float(reg.max_value),
                        "actual": actual_val
                    })
            elif reg.is_required:
                is_compliant = False
                issues.append({
                    "rule_type": rule_type.code,
                    "issue": "Missing required value",
                    "details": "This rule type is required but no actual value was provided."
                })

        # 3. Create and return report
        new_report = ComplianceReport(
            id=str(uuid.uuid4()),
            property_id=request.property_id,
            zoning_district_id=request.zoning_district_id,
            proposed_land_use_id=request.proposed_land_use_id,
            is_compliant=is_compliant,
            issues=issues,
            analyst_notes="Automated compliance check performed by Stark Compliance Engine."
        )
        
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        return new_report
