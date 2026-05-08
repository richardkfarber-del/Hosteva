from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.zoning import LandUseType, ZoningDistrict, ComplianceRuleType, ZoningRegulation
from app.schemas.zoning import LandUseTypeResponse, ZoningDistrictResponse, ComplianceRuleTypeResponse, ZoningRegulationResponse
from app.dependencies import get_api_key

router = APIRouter(prefix="/api/zoning", tags=["Zoning"], dependencies=[Depends(get_api_key)])

@router.get("/land-use-types", response_model=List[LandUseTypeResponse])
def get_land_use_types(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    limit = min(limit, 100)
    return db.query(LandUseType).offset(skip).limit(limit).all()

@router.get("/districts", response_model=List[ZoningDistrictResponse])
def get_districts(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    limit = min(limit, 100)
    return db.query(ZoningDistrict).offset(skip).limit(limit).all()

@router.get("/rule-types", response_model=List[ComplianceRuleTypeResponse])
def get_rule_types(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    limit = min(limit, 100)
    return db.query(ComplianceRuleType).offset(skip).limit(limit).all()

@router.get("/regulations", response_model=List[ZoningRegulationResponse])
def get_regulations(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    limit = min(limit, 100)
    return db.query(ZoningRegulation).offset(skip).limit(limit).all()
