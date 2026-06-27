from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Union, Any
import uuid
import json

from app.database import get_db
from app.models.compliance import MunicipalCode, Region, ZoningCode, ComplianceRule, PropertyCompliance
from app.models.property import Property

router = APIRouter(
    prefix="/api/v1/onboarding",
    tags=["onboarding"]
)

class ValidatePropertyRequest(BaseModel):
    property_id: Optional[Union[int, str]] = None
    city: str
    county: Optional[str] = None
    zip_code: str
    zoning_code: str
    property_type: str
    intended_stay_duration: Optional[str] = None
    requested_stay_duration_days: Optional[int] = None

class ChecklistItem(BaseModel):
    level: str
    authority: str
    requirement: str

class ValidatePropertyResponse(BaseModel):
    allowed: bool
    status: Optional[str] = None
    rejection_reason: Optional[str] = None
    source_url: Optional[str] = None
    checklist: Optional[List[ChecklistItem]] = None
    # Backwards compatibility / specific fields
    reason: Optional[str] = None
    warning: Optional[str] = None
    requires_permit: Optional[bool] = None
    permit_name: Optional[str] = None
    ordinance: Optional[str] = None

def clean_name(name: str) -> str:
    words = name.lower().split()
    filtered_words = [
        w for w in words
        if w not in ["city", "of", "town", "village", "county", "state", "municipality"]
    ]
    return " ".join(filtered_words)

@router.post("/validate-property", response_model=ValidatePropertyResponse)
def validate_property(request: ValidatePropertyRequest, db: Session = Depends(get_db)):
    city_lower = request.city.strip().lower()
    county_lower = (request.county or "").strip().lower()
    zip_normalized = request.zip_code.strip()
    zoning_normalized = request.zoning_code.strip().upper()
    prop_type_normalized = request.property_type.strip().lower()
    intended_stay = (request.intended_stay_duration or "").strip().lower()

    # Backwards compatibility mapping for duration
    if not intended_stay and request.requested_stay_duration_days is not None:
        if request.requested_stay_duration_days < 7:
            intended_stay = "nightly"
        elif request.requested_stay_duration_days < 30:
            intended_stay = "weekly"
        else:
            intended_stay = "monthly"

    # Hillsborough County / Tampa validation
    is_hillsborough = (
        city_lower in ["tampa", "hillsborough", "hillsborough county"] or 
        county_lower in ["hillsborough", "hillsborough county"]
    )
    if is_hillsborough:
        if intended_stay == "nightly":
            return ValidatePropertyResponse(
                allowed=False,
                status="REJECTED",
                reason="Hillsborough County Land Development Code prohibits rentals of fewer than 7 consecutive nights in standard residential zones.",
                rejection_reason="Hillsborough County Land Development Code prohibits rentals of fewer than 7 consecutive nights in standard residential zones."
            )

    # St. Petersburg validation
    is_st_pete = (
        city_lower in ["st. petersburg", "st petersburg", "st. pete", "st pete"]
    )

    # Pasco County validation
    is_pasco = (
        city_lower in ["pasco", "pasco county", "new port richey"] or 
        county_lower in ["pasco", "pasco county"]
    )

    # Generate checklist items if passes checks (or is Pasco, Hillsborough weekly/monthly, etc.)
    property_id_str = str(request.property_id) if request.property_id is not None else None
    
    if property_id_str:
        # Ensure Property exists in the DB to satisfy FK constraints
        prop = db.query(Property).filter(Property.id == property_id_str).first()
        if not prop:
            prop = Property(
                id=property_id_str,
                address=f"Onboarding Property {property_id_str}",
                city=request.city,
                state="FL",
                zip_code=request.zip_code,
                property_type=request.property_type,
                zoning_status="Pending"
            )
            db.add(prop)
            db.commit()
            db.refresh(prop)

        # Define specific compliance task checklist items
        tasks = []
        if is_hillsborough:
            tasks = [
                "Florida DBPR License task",
                "Hillsborough 6% Tourist Development Tax (TDT) registration",
                "State Sales Tax registration"
            ]
        elif is_st_pete:
            tasks = [
                "Florida DBPR License task",
                "St. Petersburg Business Tax Receipt (BTR) task",
                "Pinellas 6% TDT registration",
                "State Sales Tax registration"
            ]
        elif is_pasco:
            tasks = [
                "Pasco Conditional Use Permit task",
                "Annual Growth Management Registration",
                "Pasco 4% TDT registration",
                "State Sales Tax registration"
            ]
            
        if tasks and prop:
            prop.required_permits = json.dumps(tasks)
            db.commit()

        # Generate entries in property_compliance table
        db.query(PropertyCompliance).filter(PropertyCompliance.property_id == property_id_str).delete()
        db.commit()
        
        # Look up matched municipal code IDs
        state_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%State of Florida%")).first()
        hillsborough_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%Hillsborough County%")).first()
        st_pete_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%St. Petersburg%")).first()
        pasco_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%Pasco County%")).first()
        
        state_id = state_code.id if state_code else uuid.uuid4()
        hillsborough_id = hillsborough_code.id if hillsborough_code else uuid.uuid4()
        st_pete_id = st_pete_code.id if st_pete_code else uuid.uuid4()
        pasco_id = pasco_code.id if pasco_code else uuid.uuid4()
        
        valid_period = '[2026-06-04 00:00:00, 2027-06-04 00:00:00]'
        
        for task_name in tasks:
            if "Florida" in task_name or "State" in task_name:
                mc_id = state_id
            elif "Hillsborough" in task_name:
                mc_id = hillsborough_id
            elif "St. Petersburg" in task_name or "Pinellas" in task_name:
                mc_id = st_pete_id
            elif "Pasco" in task_name or "Annual Growth" in task_name:
                mc_id = pasco_id
            else:
                mc_id = state_id
                
            item = PropertyCompliance(
                property_id=property_id_str,
                municipal_code_id=mc_id,
                is_compliant=False,
                violation_notes=task_name,
                valid_period=valid_period
            )
            db.add(item)
        db.commit()

    # Dynamic checklists return formatting
    checklist = []
    matched_regions = db.query(Region).filter(
        (Region.locality.ilike(f"%{request.city}%")) |
        (Region.locality.ilike(f"%{request.county}%")) |
        (Region.locality.ilike(f"%{request.zip_code}%"))
    ).all()

    state_names = []
    for r in matched_regions:
        if r.admin_area:
            state_regions = db.query(Region).filter(
                (Region.admin_area == r.admin_area) &
                (~Region.locality.contains("("))
            ).all()
            for sr in state_regions:
                state_names.append(sr.locality)

    all_rules = db.query(MunicipalCode).all()
    matched_rules = []

    for rule in all_rules:
        rule_clean = clean_name(rule.municipality_name)
        is_match = False
        if rule_clean == clean_name(request.city):
            is_match = True
        elif request.county and rule_clean == clean_name(request.county):
            is_match = True
        else:
            for sn in state_names:
                if rule_clean == clean_name(sn):
                    is_match = True
                    break

        if is_match:
            matched_rules.append(rule)

    for rule in matched_rules:
        # Check zoning restrictions
        if rule.zoning_code and rule.zoning_code.strip().upper() == zoning_normalized:
            if rule.is_allowed == False:
                return ValidatePropertyResponse(
                    allowed=False,
                    status="REJECTED",
                    rejection_reason=rule.rejection_reason or f"Zoning {rule.zoning_code} is not permitted for short term rentals",
                    source_url=rule.source_url
                )
        # Check property type restrictions
        if rule.property_type and rule.property_type.strip().lower() == prop_type_normalized:
            if rule.is_allowed == False:
                return ValidatePropertyResponse(
                    allowed=False,
                    status="REJECTED",
                    rejection_reason=rule.rejection_reason or f"{rule.property_type} homes cannot be rented short term",
                    source_url=rule.source_url
                )
        # Check stay duration restrictions
        if rule.stay_restriction_days is not None and request.requested_stay_duration_days is not None:
            if request.requested_stay_duration_days < rule.stay_restriction_days:
                return ValidatePropertyResponse(
                    allowed=False,
                    status="REJECTED",
                    rejection_reason=f"Requested stay duration is less than the minimum required stay of {rule.stay_restriction_days} days",
                    source_url=rule.source_url
                )

        level = "Municipal"
        if "state" in rule.municipality_name.lower():
            level = "State"
        elif "county" in rule.municipality_name.lower():
            level = "County"

        if rule.requires_permit:
            checklist.append(ChecklistItem(
                level=level,
                authority=rule.municipality_name,
                requirement=rule.permit_name or f"Permit Required ({rule.ordinance_number})"
            ))

        if rule.tax_rate is not None:
            checklist.append(ChecklistItem(
                level=level,
                authority=rule.municipality_name,
                requirement=f"Tax Registration ({rule.tax_rate}% TDT)"
            ))

    if is_st_pete:
        return ValidatePropertyResponse(
            allowed=True,
            status="PASSED",
            warning="St. Petersburg limits short-term rentals (stays under 30 days) to 3 times per consecutive 365-day period in residential zones.",
            checklist=checklist
        )

    if is_pasco:
        return ValidatePropertyResponse(
            allowed=True,
            status="PASSED",
            requires_permit=True,
            permit_name="Conditional Use Permit (CUP)",
            checklist=checklist
        )

    return ValidatePropertyResponse(
        allowed=True,
        status="PASSED",
        checklist=checklist
    )

