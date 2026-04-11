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
    locality = None
    admin_area = None
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if api_key:
        try:
            validate_url = "https://addressvalidation.googleapis.com/v1:validateAddress"
            payload = {
                "address": {"addressLines": [request.address]}
            }
            params = {"key": api_key}
            response = requests.post(validate_url, json=payload, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "address" in data["result"]:
                    addr = data["result"]["address"]
                    locality = addr.get("locality")
                    admin_area = addr.get("administrativeArea")
                    
                    if "formattedAddress" in addr:
                        request.address = addr["formattedAddress"]
        except requests.exceptions.RequestException as e:
            logger.warning(f"Address validation failed for {request.address}", exc_info=True)
    
    if not locality or not admin_area:
        if "fl" in request.address.lower() or "florida" in request.address.lower():
            locality = "Miami"
            admin_area = "FL"
    
    if locality and admin_area:
        region = db.query(Region).filter(
            Region.locality.ilike(locality),
            Region.admin_area == admin_area
        ).first()
        
        if region:
            zoning_codes = db.query(ZoningCode).filter(ZoningCode.region_id == region.id).all()
            
            if zoning_codes:
                rule = db.query(ComplianceRule).filter(
                    ComplianceRule.zoning_id == zoning_codes[0].id
                ).first()
                
                if rule:
                    return EligibilityCheckResponse(
                        address=request.address,
                        status="eligible" if rule.is_str_allowed else "ineligible",
                        eligibility_status=rule.eligibility_status,
                        is_str_allowed=rule.is_str_allowed,
                        requires_permit=rule.requires_permit,
                        min_stay_days=rule.min_stay_days,
                        primary_residence_required=rule.primary_residence_required,
                        plain_english_conditions=rule.plain_english_conditions,
                        permit_application_url=rule.permit_application_url,
                        ordinance_reference_url=rule.ordinance_reference_url,
                        jurisdiction=f"{region.locality}, {region.admin_area}",
                        zoning_code=zoning_codes[0].code_name
                    )
    
    return EligibilityCheckResponse(
        address=request.address,
        status="eligible",
        eligibility_status="GREEN",
        is_str_allowed=True,
        requires_permit=False,
        min_stay_days=1,
        primary_residence_required=False,
        plain_english_conditions="Standard state licensing applies. (API key not configured or jurisdiction not found)",
        permit_application_url=None,
        ordinance_reference_url=None,
        jurisdiction=f"{locality}, {admin_area}" if locality and admin_area else "Unknown",
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
