from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.permit_generator import PermitApplicationRequest, PermitApplicationResponse
from app.services.permit_generator import PermitGeneratorService

router = APIRouter(
    prefix="/api/permit-generator",
    tags=["Permit Generator"]
)


@router.post("/generate", response_model=PermitApplicationResponse)
def generate_permit_application(
    request: PermitApplicationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an automated permit application for a property.
    
    This endpoint uses the FloridaComplianceEngine to evaluate property compliance
    and generates a complete permit application package with required documents,
    next steps, and compliance summary.
    
    Args:
        request: PermitApplicationRequest containing property_id
        db: Database session
        
    Returns:
        PermitApplicationResponse with generated application details
        
    Raises:
        HTTPException: If property not found or generation fails
    """
    try:
        application = PermitGeneratorService.generate_application(
            db=db,
            property_id=request.property_id
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate permit application: {str(e)}")
