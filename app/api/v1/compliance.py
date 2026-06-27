from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy.orm import Session
import uuid
import re
from datetime import date, datetime
from typing import Dict, Any, List

from app.database import get_db
from app.models.compliance import PropertyCompliance, MunicipalCode, HOARule
from app.models.property import Property
from app.models.host import Host
from app.db_models import User, Ordinance
from app.services.ocr_service import audit_compliance_document
from app.routers.properties import geocode_address
from app.schemas.compliance import AddressComplianceResponse
import os
import requests
import json

router = APIRouter(
    prefix="/api/v1/compliance",
    tags=["compliance"]
)

def generate_embedding(text: str) -> List[float]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return [0.0] * 1536
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            },
            "outputDimensionality": 1536
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data["embedding"]["values"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
    return [0.0] * 1536

@router.get("/search")
def search_compliance_ordinances(query: str, limit: int = 5, db: Session = Depends(get_db)):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")
    
    try:
        query_vector = generate_embedding(query)
        is_sqlite = "sqlite" in str(db.bind.url) if db.bind else True
        if is_sqlite:
            results = db.query(Ordinance).filter(Ordinance.ordinance_text.ilike(f"%{query}%")).limit(limit).all()
        else:
            results = db.query(Ordinance).order_by(Ordinance.embedding.cosine_distance(query_vector)).limit(limit).all()
    except Exception as e:
        print(f"pgvector query failed, falling back: {e}")
        try:
            results = db.query(Ordinance).filter(Ordinance.ordinance_text.ilike(f"%{query}%")).limit(limit).all()
        except Exception:
            results = []

            
    return [
        {
            "id": ord.id,
            "jurisdiction": ord.jurisdiction,
            "ordinance_text": ord.ordinance_text
        }
        for ord in results
    ]


def is_name_match(extracted: str, expected: str) -> bool:
    if not extracted or not expected:
        return False
    # Normalize: lowercase, remove non-alphanumeric characters
    norm_ext = re.sub(r'[^a-z0-9]', '', extracted.lower())
    norm_exp = re.sub(r'[^a-z0-9]', '', expected.lower())
    return norm_exp in norm_ext or norm_ext in norm_exp

def is_address_match(extracted: str, expected: str) -> bool:
    if not extracted or not expected:
        return False
    # Normalize: lowercase, remove non-alphanumeric characters
    norm_ext = re.sub(r'[^a-z0-9]', '', extracted.lower())
    norm_exp = re.sub(r'[^a-z0-9]', '', expected.lower())
    return norm_exp in norm_ext or norm_ext in norm_exp

@router.post("/audit-document")
async def audit_document(
    file: UploadFile = File(...),
    checklist_item_id: str = Form(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    POST /api/v1/compliance/audit-document
    Accepts:
      - file: PDF or Image compliance certificate
      - checklist_item_id: linking to property_compliance record
    Returns the evaluation status and extracted metadata.
    """
    # 1. Fetch checklist item
    try:
        try:
            uuid_val = uuid.UUID(checklist_item_id)
            checklist_item = db.query(PropertyCompliance).filter(PropertyCompliance.id == uuid_val).first()
        except Exception:
            checklist_item = db.query(PropertyCompliance).filter(PropertyCompliance.id == checklist_item_id).first()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid checklist item ID format: {e}")

    if not checklist_item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    # 2. Fetch parent property and owner details
    property_item = db.query(Property).filter(Property.id == checklist_item.property_id).first()
    if not property_item:
        raise HTTPException(status_code=404, detail="Parent property not found")

    owner = db.query(Host).filter(Host.id == property_item.user_id).first()
    owner_name = None
    if owner:
        owner_name = owner.username
    else:
        # Fallback query user model if host profile isn't present
        user_item = db.query(User).filter(User.id == property_item.user_id).first()
        if user_item:
            owner_name = user_item.email.split("@")[0]
            
    if not owner_name:
        owner_name = "Unknown Host"

    # 3. Run audit_compliance_document on file stream
    try:
        # Seek stream back to 0 just in case
        file.file.seek(0)
        expected_meta = {"owner_name": owner_name, "address": property_item.address}
        audit_res = audit_compliance_document(file.file, expected_meta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document parsing error: {e}")

    extracted_name = audit_res.get("extracted_name")
    extracted_address = audit_res.get("extracted_address")
    extracted_expiry = audit_res.get("extracted_expiration_date")

    # 4. Run comparisons
    errors = []
    if not extracted_name:
        errors.append("Owner name could not be extracted from document.")
    elif not is_name_match(extracted_name, owner_name):
        errors.append(f"Mismatched Owner Name: Document owner '{extracted_name}' does not match expected host '{owner_name}'.")

    if not extracted_address:
        errors.append("Property address could not be extracted from document.")
    elif not is_address_match(extracted_address, property_item.address):
        errors.append(f"Mismatched Address: Document address '{extracted_address}' does not match expected address '{property_item.address}'.")

    if not extracted_expiry:
        errors.append("Expiration date could not be extracted or parsed.")
    elif extracted_expiry <= date.today():
        errors.append(f"Expired Document: Compliance document expired on {extracted_expiry}.")

    # 5. Update checklist item status
    if errors:
        checklist_item.status = "REJECTED"
        checklist_item.is_compliant = False
        checklist_item.rejection_notes = " | ".join(errors)
    else:
        checklist_item.status = "APPROVED"
        checklist_item.is_compliant = True
        checklist_item.rejection_notes = None

    db.commit()
    db.refresh(checklist_item)

    return {
        "checklist_item_id": str(checklist_item.id),
        "status": checklist_item.status,
        "is_compliant": checklist_item.is_compliant,
        "rejection_notes": checklist_item.rejection_notes,
        "extracted_data": {
            "name": extracted_name,
            "address": extracted_address,
            "expiration_date": str(extracted_expiry) if extracted_expiry else None,
            "permit_number": audit_res.get("extracted_permit_number")
        }
    }

@router.get("/checklist-items/{property_id}")
def get_checklist_items(property_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    GET /api/v1/compliance/checklist-items/{property_id}
    Retrieves all compliance tasks/checklist items for a given property.
    """
    items = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == property_id).all()
    return [
        {
            "id": str(item.id),
            "property_id": item.property_id,
            "municipal_code_id": str(item.municipal_code_id),
            "is_compliant": item.is_compliant,
            "status": item.status or "PENDING",
            "rejection_notes": item.rejection_notes,
            "violation_notes": item.violation_notes,
            "valid_period": str(item.valid_period),
            "task_name": item.task_name
        }
        for item in items
    ]

@router.get("", response_model=AddressComplianceResponse)
def get_compliance_by_address(address: str, db: Session = Depends(get_db)):
    """
    GET /api/v1/compliance?address=[address]
    Resolves city, county, and state components of address using geocoding,
    queries municipal_codes and hoa_rules tables using standard SQLAlchemy,
    and returns overall compliance and matched rules details.
    """
    if not address or not address.strip():
        raise HTTPException(status_code=400, detail="Address parameter cannot be empty.")
    
    # 1. Geocode address
    try:
        geocoded = geocode_address(address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {e}")
        
    city = geocoded.get("city")
    county = geocoded.get("county")
    state = geocoded.get("state")
    
    # 2. Query municipal_codes
    municipal_code = None
    if city:
        municipal_code = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike(city),
            MunicipalCode.jurisdiction_type.ilike("City")
        ).first()
        
    if not municipal_code and county:
        clean_county = county.replace(" County", "").strip()
        municipal_code = db.query(MunicipalCode).filter(
            (MunicipalCode.municipality_name.ilike(county)) | 
            (MunicipalCode.municipality_name.ilike(clean_county)),
            MunicipalCode.jurisdiction_type.ilike("County")
        ).first()
        
    if not municipal_code and (state == "FL" or state == "Florida" or (state and state.upper() == "FL")):
        municipal_code = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike("State of Florida")
        ).first()
        
    # 3. Query hoa_rules
    hoa_rule = None
    if city or county:
        query_locations = []
        if city:
            query_locations.append(city)
        if county:
            query_locations.append(county)
            query_locations.append(county.replace(" County", "").strip())
            
        for loc in query_locations:
            hoa_rule = db.query(HOARule).filter(
                HOARule.location.ilike(f"%{loc}%")
            ).first()
            if hoa_rule:
                break
                
    # 4. Formulate checklist and compliance
    is_compliant = True
    checklist = []
    
    if municipal_code:
        if municipal_code.str_prohibited or not municipal_code.is_allowed:
            is_compliant = False
            
        if municipal_code.requires_permit:
            checklist.append({
                "task_name": municipal_code.permit_name or f"Permit Required ({municipal_code.ordinance_number})",
                "status": "PENDING",
                "is_compliant": False
            })
        if municipal_code.tax_rate is not None:
            checklist.append({
                "task_name": f"Tax Registration ({municipal_code.tax_rate}% TDT)",
                "status": "PENDING",
                "is_compliant": False
            })
            
    if hoa_rule:
        if hoa_rule.str_permitted.strip().lower() == "no":
            is_compliant = False
            
        checklist.append({
            "task_name": f"HOA Registration: {hoa_rule.hoa_name}",
            "status": "PENDING",
            "is_compliant": False
        })
        
    if not city and not county and not state:
        raise HTTPException(status_code=404, detail="No compliance rules found for this address location.")

    return AddressComplianceResponse(
        address=address,
        is_compliant=is_compliant,
        municipal_code=municipal_code,
        hoa_rule=hoa_rule,
        checklist=checklist
    )


@router.get("/tasks/{task_id}")
def get_compliance_task(task_id: str, db: Session = Depends(get_db)):
    from app.models.compliance import PropertyCompliance, MunicipalCode
    from app.models.property import Property
    import uuid
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    task = db.query(PropertyCompliance).filter(PropertyCompliance.id == task_uuid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Compliance task not found")
        
    prop = db.query(Property).filter(Property.id == task.property_id).first()
    m_code = db.query(MunicipalCode).filter(MunicipalCode.id == task.municipal_code_id).first()
    
    # Generate what to upload and description based on task_name
    task_name = task.task_name or task.violation_notes or "Required Permit"
    description = ""
    what_to_upload = ""
    instructions = ""
    
    if "Pasco Conditional Use Permit" in task_name:
        description = "Obtain Pasco Conditional Use Permit"
        what_to_upload = "Official Pasco County CUP certificate, approved site plan, or tax receipt showing the permit number."
        instructions = "To satisfy the Pasco Conditional Use Permit requirement, please upload your official Pasco County CUP certificate, approved site plan, or tax collector receipt showing the permit number."
    elif "Pasco 4%" in task_name:
        description = "Pasco 4% Tourist Development Tax (TDT) registration"
        what_to_upload = "Pasco County TDT tax account statement, receipt, or registration document."
        instructions = "Please upload your Pasco County TDT certificate showing your 6-digit TDT account number with Pasco County named as authority."
    elif "State Sales Tax" in task_name:
        description = "State Sales Tax registration"
        what_to_upload = "Florida Department of Revenue Certificate of Registration (Form DR-11)."
        instructions = "Please upload your Florida DR-11 Certificate of Registration showing your active Sales Tax registration details."
    elif "Hillsborough 6%" in task_name:
        description = "Hillsborough 6% Tourist Development Tax (TDT) registration"
        what_to_upload = "Hillsborough County TDT certificate or receipt."
        instructions = "Please upload your Hillsborough County TDT certificate showing your TDT account registration."
    elif "St. Petersburg" in task_name:
        description = "St. Petersburg Business Tax Receipt (BTR)"
        what_to_upload = "St. Petersburg Business Tax Receipt document."
        instructions = "Please upload your St. Petersburg BTR showing active short-term rental approval."
    elif "Pinellas" in task_name:
        description = "Pinellas 6% TDT registration"
        what_to_upload = "Pinellas County TDT certificate or receipt."
        instructions = "Please upload your Pinellas County TDT certificate showing registration."
    elif "Florida DBPR" in task_name:
        description = "Florida DBPR License"
        what_to_upload = "Florida DBPR License Certificate."
        instructions = "Please upload your active Florida DBPR license certificate for transient public lodging."
    else:
        description = task_name
        what_to_upload = "Official registration, receipt, or certificate document."
        instructions = f"Please upload the official document or certificate matching {task_name}."

    return {
        "id": str(task.id),
        "property_id": task.property_id,
        "property_address": prop.address if prop else "Unknown Address",
        "task_name": task_name,
        "description": description,
        "what_to_upload": what_to_upload,
        "instructions": instructions,
        "status": task.status or "PENDING",
        "is_compliant": task.is_compliant,
        "uploaded_file_url": task.uploaded_file_url,
        "ocr_metadata_json": task.ocr_metadata_json,
        "verification_notes": task.verification_notes
    }


from fastapi import UploadFile, File
import shutil
import os

@router.post("/tasks/{task_id}/upload")
def upload_compliance_task_file(
    task_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    from app.models.compliance import PropertyCompliance
    import uuid
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    task = db.query(PropertyCompliance).filter(PropertyCompliance.id == task_uuid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Compliance task not found")
        
    # Create static upload folder
    upload_dir = "app/static/uploaded_permits"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    safe_filename = f"{task_id}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update properties_compliance
    task.uploaded_file_url = f"/static/uploaded_permits/{safe_filename}"
    task.status = "PENDING"
    task.is_compliant = False
    task.verification_notes = "AI document auditing is in progress..."
    db.commit()
    
    # Dispatch Celery task process_document_ocr
    from app.tasks.audit import process_document_ocr
    process_document_ocr.delay(str(task.id), task.uploaded_file_url)
    
    return {
        "status": "PENDING",
        "uploaded_file_url": task.uploaded_file_url,
        "message": "File uploaded successfully. Document audit started."
    }


@router.get("/tasks/{task_id}/status")
def get_compliance_task_status(task_id: str, db: Session = Depends(get_db)):
    from app.models.compliance import PropertyCompliance
    import uuid
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    task = db.query(PropertyCompliance).filter(PropertyCompliance.id == task_uuid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Compliance task not found")
        
    import json
    ocr_result = None
    if task.ocr_metadata_json:
        try:
            ocr_result = json.loads(task.ocr_metadata_json)
        except Exception:
            pass
            
    return {
        "status": task.status or "PENDING",
        "is_compliant": task.is_compliant,
        "verification_notes": task.verification_notes,
        "ocr_result": ocr_result
    }


