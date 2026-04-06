from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.zoning import ComplianceCheckRequest, ComplianceReportResponse
from app.services.compliance_engine import ComplianceEngine
from app.dependencies import get_api_key

router = APIRouter(prefix="/api/compliance", tags=["Compliance"], dependencies=[Depends(get_api_key)])

@router.post("/check", response_model=ComplianceReportResponse)
def run_compliance_check(request: ComplianceCheckRequest, db: Session = Depends(get_db)):
    # 1. Basic validation of input (handled by Pydantic schemas)
    # 2. Run engine
    report = ComplianceEngine.evaluate(db, request)
    return report
