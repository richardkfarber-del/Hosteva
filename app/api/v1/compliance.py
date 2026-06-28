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
    state_code = state.strip() if state else ""
    if len(state_code) > 2:
        state_map = {
            "florida": "FL", "california": "CA", "texas": "TX", "new york": "NY",
            "colorado": "CO", "hawaii": "HI", "georgia": "GA", "north carolina": "NC",
            "tennessee": "TN", "arizona": "AZ"
        }
        state_code = state_map.get(state_code.lower(), state_code)

    if city:
        municipal_code = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike(city),
            MunicipalCode.jurisdiction_type.ilike("City"),
            ((MunicipalCode.state.ilike(state_code)) | (MunicipalCode.state.is_(None)))
        ).first()
        
    if not municipal_code and county:
        clean_county = county.replace(" County", "").strip()
        municipal_code = db.query(MunicipalCode).filter(
            (MunicipalCode.municipality_name.ilike(county)) | 
            (MunicipalCode.municipality_name.ilike(clean_county)),
            MunicipalCode.jurisdiction_type.ilike("County"),
            ((MunicipalCode.state.ilike(state_code)) | (MunicipalCode.state.is_(None)))
        ).first()
        
    if not municipal_code and (state_code.upper() == "FL" or not state_code):
        municipal_code = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike("State of Florida"),
            ((MunicipalCode.state.ilike("FL")) | (MunicipalCode.state.is_(None)))
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

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TaskChatRequest(BaseModel):
    query: str

@router.post("/tasks/{task_id}/chat")
def compliance_task_chat(
    task_id: str,
    payload: TaskChatRequest,
    db: Session = Depends(get_db)
):
    from app.models.compliance import PropertyCompliance, MunicipalCode
    from app.models.property import Property
    import uuid
    import json
    
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    task = db.query(PropertyCompliance).filter(PropertyCompliance.id == task_uuid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Compliance task not found")
        
    prop = db.query(Property).filter(Property.id == task.property_id).first()
    task_name = task.task_name or task.violation_notes or "Required Permit"
    
    query_lower = payload.query.lower()
    
    # Custom intelligence responses
    response_text = ""
    links = []
    prefill_data = {}
    
    if prop:
        prefill_data = {
            "owner_name": "Richard Farber",
            "property_address": prop.address,
            "city": prop.city,
            "state": prop.state,
            "zip_code": prop.zip_code,
            "parcel_id": "55-23-19-0000-00100-0020"
        }
    
    if "pasco conditional" in task_name.lower():
        response_text = (
            "A **Conditional Use Permit (CUP)** is a zoning approval required by Pasco County to operate a short-term rental "
            "in standard residential districts. To obtain a CUP, you must submit an application packet containing:\n\n"
            "1. A completed Pasco County CUP Application form.\n"
            "2. A detailed **site plan** showing all off-street parking spaces (minimum 2 required).\n"
            "3. A standard floor plan of the property.\n"
            "4. A non-refundable application fee of **$250**.\n\n"
            "Once submitted, your application is reviewed by the Planning Commission. Hosteva can pre-fill this application for you!"
        )
        links = [
            {"label": "Pasco County Planning & Development Portal", "url": "https://www.pascocountyfl.gov/373/Planning-Development"},
            {"label": "Official Pasco CUP Application Guidelines (Accela Citizen Portal)", "url": "https://aca.accela.com/PASC/"}
        ]
    elif "annual growth" in task_name.lower():
        response_text = (
            "The **Annual Growth Management Registration** is a required yearly registration for all short-term rental "
            "properties operating in Pasco County. This ensures that rentals comply with emergency contact and safety guidelines.\n\n"
            "**Requirements to apply**:\n"
            "1. An active Florida DBPR lodging license.\n"
            "2. A local emergency contact available 24/7 who lives within 30 miles.\n"
            "3. An annual fee of **$150**.\n\n"
            "You can complete this registration completely online through the Pasco County Customer Service portal."
        )
        links = [
            {"label": "Pasco County Growth Management Department", "url": "https://www.pascocountyfl.gov/263/Growth-Management"},
            {"label": "Online Registration Form (Accela Citizen Portal)", "url": "https://aca.accela.com/PASC/"}
        ]
    elif "hillsborough" in task_name.lower():
        response_text = (
            "Hillsborough County requires short-term lodging operators to register for a **Tourist Development Tax (TDT) Account** "
            "to collect and remit the county's **6% tourist tax** on all stays under 183 days.\n\n"
            "**Registration Steps**:\n"
            "1. Visit the Hillsborough County Tax Collector's website.\n"
            "2. Register online for a new Tourist Development Tax account.\n"
            "3. You will need your property parcel ID, owner details, and DBPR license details (if obtained)."
        )
        links = [
            {"label": "Hillsborough County Tax Collector TDT Portal", "url": "https://www.hillstax.org/taxes/tourist-development-tax/"}
        ]
    elif "florida dbpr" in task_name.lower():
        response_text = (
            "The **Florida DBPR Transient Public Lodging License** is a state-level requirement for anyone renting out an entire "
            "single-family home, condo, or townhouse as a short-term rental.\n\n"
            "**Steps to obtain**:\n"
            "1. Create an account on the DBPR Online Services portal.\n"
            "2. Complete application **Form DBPR HR-7020**.\n"
            "3. Pay the license fee (typically ~$150 depending on unit count).\n"
            "4. Schedule the mandatory sanitation and safety inspection."
        )
        links = [
            {"label": "Florida DBPR Online Services Portal", "url": "https://www.myfloridalicense.com/dbpr/"}
        ]
    elif "st. petersburg" in task_name.lower():
        response_text = (
            "The City of St. Petersburg requires all short-term rental hosts to obtain an annual **Business Tax Receipt (BTR)** "
            "to operate lawfully. Note that St. Petersburg limits short-term rentals in standard residential zones to 3 times per 365-day period.\n\n"
            "**How to apply**:\n"
            "1. Submit a Business Tax Receipt application to the City's Billing & Collections department.\n"
            "2. Provide your Pinellas County Tourist Development Tax (TDT) account number.\n"
            "3. Pay the local business tax fee (~$95)."
        )
        links = [
            {"label": "St. Petersburg BTR Application Portal", "url": "https://www.stpete.org/business/business_tax_receipts/"}
        ]
    elif "pinellas" in task_name.lower():
        response_text = (
            "Pinellas County requires short-term rental operators to register for a **Tourist Development Tax (TDT) Account** "
            "to collect and remit the county's **6% tourist tax** on all tourist accommodations.\n\n"
            "**How to apply**:\n"
            "1. Open the Pinellas County Tax Collector portal.\n"
            "2. Complete the online Tourist Development Tax registration form.\n"
            "3. Submit owner and property parcel information."
        )
        links = [
            {"label": "Pinellas County Tax Collector TDT Portal", "url": "https://www.pinellastaxcollector.gov/"}
        ]
    elif "state sales tax" in task_name.lower():
        response_text = (
            "The State of Florida requires all short-term rental hosts to register with the Florida Department of Revenue "
            "to collect and remit **6% State Sales Tax** and any local discretionary sales surtaxes.\n\n"
            "**How to register**:\n"
            "1. Visit the Florida Department of Revenue's e-Services portal.\n"
            "2. Complete the **Florida Business Tax Application (Form DR-1)**.\n"
            "3. Receive your Certificate of Registration (Form DR-11) by mail or online portal download."
        )
        links = [
            {"label": "Florida Department of Revenue e-Services", "url": "https://floridarevenue.com/taxes/taxesfees/Pages/sales_tax.aspx"}
        ]
    else:
        response_text = (
            f"To satisfy the compliance task for **{task_name}**, you must obtain the official approval or registration document from the local authority.\n\n"
            "Please follow the county or city guidelines to submit your application. You can upload the receipt or certificate here once obtained."
        )
        links = [
            {"label": "Florida Municipal Codes Directory", "url": "https://www.myflorida.com/"}
        ]
        
    if "cost" in query_lower or "fee" in query_lower or "price" in query_lower:
        if "pasco conditional" in task_name.lower():
            response_text = "The application fee for the Pasco County Conditional Use Permit (CUP) is **$250**."
        elif "annual growth" in task_name.lower():
            response_text = "The registration fee for the Pasco County Annual Growth Management Registration is **$150** annually."
        elif "st. petersburg" in task_name.lower():
            response_text = "The St. Petersburg Business Tax Receipt (BTR) fee is approximately **$95**."
        elif "florida dbpr" in task_name.lower():
            response_text = "The Florida DBPR Transient Public Lodging license fee is approximately **$150** for a single unit."
        else:
            response_text = "The application fee varies depending on your municipal authority. Typically it ranges between $50 and $250."
            
    return {
        "response": response_text,
        "links": links,
        "prefill_data": prefill_data
    }

from pydantic import BaseModel
class AgentTriggerRequest(BaseModel):
    property_id: str
    city: str
    county: str
    state: str

@router.post("/agent/trigger", status_code=202)
def trigger_agent_compliance_scraper(
    payload: AgentTriggerRequest,
    db: Session = Depends(get_db)
):
    # Check if a temporary MunicipalCode record exists; if not, create one
    temp_mc = db.query(MunicipalCode).filter(
        MunicipalCode.municipality_name.ilike(payload.city),
        MunicipalCode.state.ilike(payload.state)
    ).first()
    
    if not temp_mc:
        temp_mc = MunicipalCode(
            municipality_name=payload.city,
            jurisdiction_type="City",
            ordinance_number="PENDING-SCRAPE",
            str_prohibited=False,
            is_allowed=True,
            requires_permit=True,
            state=payload.state,
            is_ai_scraped=True,
            is_expert_verified=False
        )
        db.add(temp_mc)
        db.commit()
        db.refresh(temp_mc)
        
    from app.tasks.scraper import run_agent_compliance_scraper
    run_agent_compliance_scraper.delay(
        payload.property_id,
        payload.city,
        payload.county,
        payload.state
    )
    
    return {
        "property_id": payload.property_id,
        "status": "SCRAPING_ACTIVE",
        "message": "Zoning rules not found in pre-compiled database. Initiating Real-time AI Scraper Agent."
    }

@router.post("/tasks/{id}/fill-permit")
def fill_permit_form(
    id: str,
    db: Session = Depends(get_db)
):
    import zipfile
    import io
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    task_uuid = uuid.UUID(id) if isinstance(id, str) and "-" in id else id
    task = db.query(PropertyCompliance).filter(PropertyCompliance.id == task_uuid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Compliance task not found")
        
    property_obj = db.query(Property).filter(Property.id == task.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
        
    host_obj = db.query(Host).filter(Host.id == property_obj.user_id).first()
    if not host_obj:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    mc = db.query(MunicipalCode).filter(MunicipalCode.id == task.municipal_code_id).first()
    if not mc:
        raise HTTPException(status_code=404, detail="Municipal rules not found")
        
    # Check if we should fall back to direct portal link if no rules source is present
    if not mc.source_url and not mc.tax_rate_registration_fee:
        return {
            "status": "FAILED",
            "warning": "Zoning application form template is not available for this county yet.",
            "source_url": "https://www.myflorida.com/"
        }
        
    # Local path for template PDF
    template_dir = "app/static/templates"
    os.makedirs(template_dir, exist_ok=True)
    template_filename = f"template_{mc.state}_{mc.municipality_name.replace(' ', '_')}.pdf"
    template_path = os.path.join(template_dir, template_filename)
    
    # 1. Ensure a template file exists dynamically
    if not os.path.exists(template_path):
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        c = canvas.Canvas(template_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 700, "SHORT-TERM RENTAL LICENSE APPLICATION")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 680, f"Authority: {mc.municipality_name} ({mc.state})")
        c.setFont("Helvetica", 10)
        c.drawString(100, 660, f"Document Reference: STR-REG-{mc.state}-{mc.municipality_name.replace(' ', '').upper()}")
        
        c.drawString(100, 600, "1. APPLICANT / HOST NAME:")
        c.drawString(100, 550, "2. PROPERTY LOCATION ADDRESS:")
        c.drawString(100, 500, "3. CONTACT EMAIL ADDRESS:")
        c.drawString(100, 450, "4. TAX ID / REGISTRATION REF:")
        c.drawString(100, 300, "Applicant Signature: _______________________")
        c.drawString(400, 300, "Date: _________________")
        c.save()
        
    # 2. Parse form layout mappings or use default coordinate mappings
    layout_data = {}
    if mc.form_layout_json:
        try:
            layout_data = json.loads(mc.form_layout_json)
        except:
            pass
            
    # Default layout coordinates if none specified in DB
    if not layout_data:
        layout_data = {
            "flat": {
                "pages": [
                    {
                        "page_number": 0,
                        "fields": [
                            {"x": 300, "y": 600, "value_type": "host_name"},
                            {"x": 300, "y": 550, "value_type": "property_address"},
                            {"x": 300, "y": 500, "value_type": "host_email"},
                            {"x": 300, "y": 450, "value_type": "tax_id"}
                        ]
                    }
                ]
            }
        }
        
    host_name = getattr(host_obj, "owner_name", None) or host_obj.username or "Richard Farber"
    property_address = property_obj.address
    host_email = host_obj.email or "host@example.com"
    tax_id = f"TX-ID-{mc.state}-{id[:8].upper()}"
    
    # 3. Create pre-filled overlay PDF
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)
    
    flat_config = layout_data.get("flat", {})
    for page in flat_config.get("pages", []):
        if page.get("page_number") == 0:
            for field in page.get("fields", []):
                x = field.get("x")
                y = field.get("y")
                v_type = field.get("value_type")
                val = ""
                if v_type == "host_name":
                    val = host_name
                elif v_type == "property_address":
                    val = property_address
                elif v_type == "host_email":
                    val = host_email
                elif v_type == "tax_id":
                    val = tax_id
                can.drawString(x, y, val)
    can.save()
    
    packet.seek(0)
    new_pdf = PdfReader(packet)
    
    # 4. Merge overlay with template
    existing_pdf = PdfReader(template_path)
    output_writer = PdfWriter()
    
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output_writer.add_page(page)
    
    for i in range(1, len(existing_pdf.pages)):
        output_writer.add_page(existing_pdf.pages[i])
        
    filled_pdf_bytes = io.BytesIO()
    output_writer.write(filled_pdf_bytes)
    filled_pdf_bytes.seek(0)
    
    # 5. Generate Instruction Sheet PDF dynamically summarizing rules
    instruction_bytes = io.BytesIO()
    c_inst = canvas.Canvas(instruction_bytes, pagesize=letter)
    c_inst.setFont("Helvetica-Bold", 18)
    c_inst.drawString(100, 720, "Hosteva Short-Term Rental Seeding & Guide")
    c_inst.setFont("Helvetica-Bold", 14)
    c_inst.drawString(100, 690, f"Jurisdiction: {mc.municipality_name}, {mc.state}")
    
    c_inst.setFont("Helvetica", 10)
    c_inst.drawString(100, 650, f"Permit/License Required: {'Yes' if mc.requires_permit else 'No'}")
    c_inst.drawString(100, 630, f"Minimum Stay Requirement: {mc.minimum_stay_requirement or 'None'}")
    c_inst.drawString(100, 610, f"Occupancy Limits: {mc.occupancy_limits or 'Not specified'}")
    c_inst.drawString(100, 590, f"Tax & Fees Details: {mc.tax_rate_registration_fee or 'Not specified'}")
    c_inst.drawString(100, 570, f"Official Guidelines Portal: {mc.source_url or 'None'}")
    
    c_inst.setFont("Helvetica-Bold", 12)
    c_inst.drawString(100, 520, "Submission Instructions:")
    c_inst.setFont("Helvetica", 10)
    c_inst.drawString(100, 500, "1. Download the pre-filled application form from this package.")
    c_inst.drawString(100, 480, "2. Review the details, sign, and date the form.")
    c_inst.drawString(100, 460, "3. Submit the form to the official county guidelines portal listed above.")
    c_inst.drawString(100, 440, "4. Upload the issued license certificate to Hosteva dashboard to verify compliance.")
    
    c_inst.save()
    instruction_bytes.seek(0)
    
    # 6. Compress both PDFs into a single ZIP archive saved locally
    static_gen_dir = "app/static/generated_permits"
    os.makedirs(static_gen_dir, exist_ok=True)
    zip_filename = f"permit_{task.id}_pkg.zip"
    zip_filepath = os.path.join(static_gen_dir, zip_filename)
    
    with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
        zip_file.writestr("permit_application.pdf", filled_pdf_bytes.getvalue())
        zip_file.writestr("submission_instructions.pdf", instruction_bytes.getvalue())
        
    return {
        "download_url": f"/static/generated_permits/{zip_filename}",
        "status": "READY"
    }


