from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
from app.database import get_db

logger = logging.getLogger(__name__)
from app.models.compliance import Region, ZoningCode, ComplianceRule
from app.schemas.compliance import (
    RegionCreate, RegionResponse,
    ZoningCodeCreate, ZoningCodeResponse,
    ComplianceRuleCreate, ComplianceRuleResponse,
    EligibilityCheckRequest, EligibilityCheckResponse
)
import os
import requests

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])

@router.post("/eligibility-check", response_model=EligibilityCheckResponse)
def check_eligibility(request: EligibilityCheckRequest, db: Session = Depends(get_db)):
    from app.routers.properties import geocode_address
    from app.services.compliance import run_gemini_audit

    logger.info(f"Compliance Router: Starting eligibility check for address: {request.address}")
    
    # 1. Geocode the address using Google Maps Geocoding API to resolve locality components
    geocoded = geocode_address(request.address)
    city_name = geocoded.get("city")
    county_name = geocoded.get("county")
    state_name = geocoded.get("state")
    address_components = geocoded.get("address_components")

    # Simple local fallback parsing if geocoding returns empty values (e.g., when API key is missing or invalid)
    if not city_name or not state_name:
        parts = [p.strip() for p in request.address.split(",")]
        if len(parts) >= 3:
            city_name = city_name or parts[-2]
            state_zip = parts[-1].split()
            if state_zip:
                state_name = state_name or state_zip[0]
        else:
            city_name = city_name or "Miami"
            state_name = state_name or "FL"
    if not county_name:
        county_name = f"{city_name} County"

    # 2. Execute the real Gemini Compliance Audit
    audit_results = run_gemini_audit(
        city=city_name,
        county=county_name,
        state=state_name,
        address=request.address,
        address_components=address_components
    )

    # 3. Map Gemini results to EligibilityCheckResponse structure
    status_raw = audit_results.get("eligibility_status", "Pending")
    status_upper = status_raw.upper()

    if status_upper == "COMPLIANT":
        eligibility_status = "GREEN"
        status = "eligible"
        is_str_allowed = True
    elif status_upper == "VIOLATION":
        eligibility_status = "RED"
        status = "ineligible"
        is_str_allowed = False
    elif status_upper in ("PENDING", "ACTION REQUIRED"):
        eligibility_status = "YELLOW"
        status = "eligible"
        is_str_allowed = True
    else:
        eligibility_status = "YELLOW"
        status = "eligible"
        is_str_allowed = True

    # 4. Intelligent day and flag parsing from local restrictions
    min_stay_days = 1
    primary_residence_required = False
    local_rest = audit_results.get("local_restrictions", {}) or {}
    
    text_to_search = ""
    for k, v in local_rest.items():
        if v:
            text_to_search += f" {k} {v}".lower()

    if "three (3) consecutive months" in text_to_search or "3 months" in text_to_search or "90 days" in text_to_search or "three-month" in text_to_search:
        min_stay_days = 90
    elif "30 days" in text_to_search or "monthly" in text_to_search or "one month" in text_to_search:
        min_stay_days = 30
    elif "7 days" in text_to_search or "weekly" in text_to_search:
        min_stay_days = 7

    if "primary residence" in text_to_search:
        primary_residence_required = True

    requires_permit = len(audit_results.get("required_permits", [])) > 0

    conditions_list = []
    for k, v in local_rest.items():
        if v:
            conditions_list.append(f"{k}: {v}")
    
    plain_english_conditions = " | ".join(conditions_list) if conditions_list else "Standard state licensing applies."

    return EligibilityCheckResponse(
        address=request.address,
        status=status,
        eligibility_status=eligibility_status,
        is_str_allowed=is_str_allowed,
        requires_permit=requires_permit,
        min_stay_days=min_stay_days,
        primary_residence_required=primary_residence_required,
        plain_english_conditions=plain_english_conditions,
        permit_application_url="https://www.myfloridalicense.com/dbpr/",
        ordinance_reference_url=None,
        jurisdiction=f"{city_name}, {state_name}",
        zoning_code=None
    )

@router.post("/regions", response_model=RegionResponse)
def create_region(region: RegionCreate, db: Session = Depends(get_db)):
    existing = db.query(Region).filter(
        Region.locality == region.locality,
        Region.admin_area == region.admin_area
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Region already exists")
    
    db_region = Region(locality=region.locality, admin_area=region.admin_area)
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region

@router.get("/regions", response_model=list[RegionResponse])
def list_regions(db: Session = Depends(get_db)):
    return db.query(Region).all()

@router.post("/zoning-codes", response_model=ZoningCodeResponse)
def create_zoning_code(zoning: ZoningCodeCreate, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.id == zoning.region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    db_zoning = ZoningCode(
        region_id=zoning.region_id,
        code_name=zoning.code_name,
        description=zoning.description
    )
    db.add(db_zoning)
    db.commit()
    db.refresh(db_zoning)
    return db_zoning

@router.get("/regions/{region_id}/zoning-codes", response_model=list[ZoningCodeResponse])
def list_zoning_codes(region_id: str, db: Session = Depends(get_db)):
    return db.query(ZoningCode).filter(ZoningCode.region_id == region_id).all()

@router.post("/compliance-rules", response_model=ComplianceRuleResponse)
def create_compliance_rule(rule: ComplianceRuleCreate, db: Session = Depends(get_db)):
    zoning = db.query(ZoningCode).filter(ZoningCode.id == rule.zoning_id).first()
    if not zoning:
        raise HTTPException(status_code=404, detail="Zoning code not found")
    
    db_rule = ComplianceRule(
        zoning_id=rule.zoning_id,
        eligibility_status=rule.eligibility_status,
        is_str_allowed=rule.is_str_allowed,
        requires_permit=rule.requires_permit,
        min_stay_days=rule.min_stay_days,
        primary_residence_required=rule.primary_residence_required,
        plain_english_conditions=rule.plain_english_conditions,
        permit_application_url=rule.permit_application_url,
        ordinance_reference_url=rule.ordinance_reference_url
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.get("/zoning-codes/{zoning_id}/compliance-rules", response_model=list[ComplianceRuleResponse])
def list_compliance_rules(zoning_id: str, db: Session = Depends(get_db)):
    return db.query(ComplianceRule).filter(ComplianceRule.zoning_id == zoning_id).all()

@router.post("/seed-miami")
def seed_miami_data(db: Session = Depends(get_db)):
    existing = db.query(Region).filter(
        Region.locality == "Miami",
        Region.admin_area == "FL"
    ).first()
    if existing:
        return {"message": "Miami data already seeded"}
    
    region = Region(locality="Miami", admin_area="FL")
    db.add(region)
    db.commit()
    db.refresh(region)
    
    zoning_codes_data = [
        {"code": "T3", "description": "Residential Medium Density"},
        {"code": "T4", "description": "Residential High Density"},
        {"code": "T5", "description": "Mixed Use"},
        {"code": "C", "description": "Commercial"}
    ]
    
    for zdata in zoning_codes_data:
        zoning = ZoningCode(region_id=region.id, code_name=zdata["code"], description=zdata["description"])
        db.add(zoning)
    
    db.commit()
    
    rules_data = [
        {"zoning_code": "T3", "eligibility_status": "RED", "is_str_allowed": False, "requires_permit": True, "min_stay_days": 30, "primary_residence_required": True, "plain_english_conditions": "STR prohibited. Must be primary residence only."},
        {"zoning_code": "T4", "eligibility_status": "YELLOW", "is_str_allowed": True, "requires_permit": True, "min_stay_days": 7, "primary_residence_required": True, "plain_english_conditions": "STR allowed with permit. Primary residence required. Min 7-day stay."},
        {"zoning_code": "T5", "eligibility_status": "GREEN", "is_str_allowed": True, "requires_permit": True, "min_stay_days": 1, "primary_residence_required": False, "plain_english_conditions": "STR fully permitted with Miami-Dade BTR permit."},
        {"zoning_code": "C", "eligibility_status": "GREEN", "is_str_allowed": True, "requires_permit": True, "min_stay_days": 1, "primary_residence_required": False, "plain_english_conditions": "Commercial zones permit STR with standard business license."}
    ]
    
    all_zoning = db.query(ZoningCode).filter(ZoningCode.region_id == region.id).all()
    zoning_map = {z.code_name: z.id for z in all_zoning}
    
    for rdata in rules_data:
        rule = ComplianceRule(
            zoning_id=zoning_map[rdata["zoning_code"]],
            eligibility_status=rdata["eligibility_status"],
            is_str_allowed=rdata["is_str_allowed"],
            requires_permit=rdata["requires_permit"],
            min_stay_days=rdata["min_stay_days"],
            primary_residence_required=rdata["primary_residence_required"],
            plain_english_conditions=rdata["plain_english_conditions"],
            permit_application_url="https://www.miamigov.com/michaelbusinesscenter",
            ordinance_reference_url="https://library.municode.com/fl/miami_dade_county/codes/code_of_ordinances?nodeId=PTIIORCO_CH33ZORE"
        )
        db.add(rule)
    
    db.commit()
    
    return {"message": "Miami pilot data seeded successfully"}
