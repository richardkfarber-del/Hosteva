from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.permit_generator import PermitApplicationRequest, PermitApplicationResponse
from app.services.permit_generator import PermitGeneratorService, PermitNotApplicableError

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

    Uses beds (preferred) / bedrooms-safe attribute access so attribute mismatch
    never 500s. Returns 422 when PERMIT is N/A (Under Review / no-permit).
    """
    try:
        application = PermitGeneratorService.generate_application(
            db=db,
            property_id=request.property_id
        )
        return application
    except PermitNotApplicableError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AttributeError as e:
        # Should not happen after beds/bedrooms fix; keep honest 500 detail if it does.
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate permit application: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate permit application: {str(e)}",
        )
