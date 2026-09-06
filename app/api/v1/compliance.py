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

            
    import os as _os
    is_prod = _os.getenv("ENVIRONMENT", "").lower() == "production"
    out = []
    for ord in results:
        jur = (ord.jurisdiction or "")
        # Never surface labeled sample/demo ordinances to users (esp. production)
        if "sample" in jur.lower() or "(sample)" in jur.lower() or "demo" in jur.lower():
            if is_prod or True:  # Phase A: hide in all envs for user-facing search
                continue
        out.append({
            "id": ord.id,
            "jurisdiction": ord.jurisdiction,
            "ordinance_text": ord.ordinance_text
        })
    return out


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

from app.core.security import get_current_user
@router.get("/checklist-items/{property_id}")
def get_checklist_items(property_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """
    GET /api/v1/compliance/checklist-items/{property_id}
    Retrieves all compliance tasks/checklist items for a given property.
    """
    from app.models.host import Host
    from app.core.billing_gate import host_has_active_essentials, require_active_essentials

    try:
        host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    except Exception:
        host = None
    # US-006: Active Essentials — must 403 (never 500) when Free
    require_active_essentials(db, host)

    items = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == property_id).all()
    # Prefetch municipal source URLs for checklist citation (US-003)
    mc_ids = {item.municipal_code_id for item in items if item.municipal_code_id}
    mc_by_id = {}
    if mc_ids:
        for mc in db.query(MunicipalCode).filter(MunicipalCode.id.in_(list(mc_ids))).all():
            mc_by_id[mc.id] = mc
    result = []
    for item in items:
        mc = mc_by_id.get(item.municipal_code_id)
        result.append({
            "id": str(item.id),
            "property_id": item.property_id,
            "municipal_code_id": str(item.municipal_code_id) if item.municipal_code_id else None,
            "is_compliant": item.is_compliant,
            "status": item.status or "PENDING",
            "rejection_notes": item.rejection_notes,
            "violation_notes": item.violation_notes,
            "valid_period": str(item.valid_period),
            "task_name": item.task_name,
            "source_url": (mc.source_url if mc and mc.source_url else None),
        })
    return result

@router.get("", response_model=AddressComplianceResponse)
@router.get("/address", response_model=AddressComplianceResponse)
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
        # Alias: packs may store "City of Miami Beach" while geocode returns "Miami Beach"
        if not municipal_code:
            municipal_code = db.query(MunicipalCode).filter(
                MunicipalCode.municipality_name.ilike(f"City of {city}"),
                MunicipalCode.jurisdiction_type.ilike("City"),
                ((MunicipalCode.state.ilike(state_code)) | (MunicipalCode.state.is_(None)))
            ).first()
        if not municipal_code:
            municipal_code = db.query(MunicipalCode).filter(
                MunicipalCode.municipality_name.ilike(city),
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
            
        muni_source = municipal_code.source_url or None
        if municipal_code.requires_permit:
            checklist.append({
                "task_name": municipal_code.permit_name or f"Permit Required ({municipal_code.ordinance_number})",
                "status": "PENDING",
                "is_compliant": False,
                "source_url": muni_source,
            })
        if municipal_code.tax_rate is not None:
            checklist.append({
                "task_name": f"Tax Registration ({municipal_code.tax_rate}% TDT)",
                "status": "PENDING",
                "is_compliant": False,
                "source_url": muni_source,
            })
            
    if hoa_rule:
        if hoa_rule.str_permitted.strip().lower() == "no":
            is_compliant = False
            
        checklist.append({
            "task_name": f"HOA Registration: {hoa_rule.hoa_name}",
            "status": "PENDING",
            "is_compliant": False,
            "source_url": hoa_rule.official_website or None,
        })
        
    if not city and not county and not state:
        raise HTTPException(status_code=404, detail="No compliance rules found for this address location.")

    # Covered gate (SP-006/007/010): Curated Free Audit = FL + usable municipal row.
    # Non-FL Complete rows may exist as Thin/research seed but never elevate Covered.
    # HOA match alone never elevates Covered. AI drafts (is_ai_scraped) never Covered.
    is_under_review = False
    status_reason = None
    coverage_tier = None

    state_upper = (state_code or "").strip().upper()
    is_fl = state_upper == "FL"

    def _is_curated_fl(mc) -> bool:
        if not mc:
            return False
        if not is_fl:
            return False
        mc_state = (mc.state or "FL").strip().upper()
        if mc_state and mc_state != "FL":
            return False
        if getattr(mc, "is_ai_scraped", False):
            return False
        if mc.municipality_name == "State of Florida" and city and city.lower() != "florida":
            return False
        return True

    if not municipal_code:
        is_under_review = True
        status_reason = "MISSING_MUNICIPAL_CODE"
        coverage_tier = "UNDER_REVIEW"
    elif not _is_curated_fl(municipal_code):
        is_under_review = True
        if not is_fl:
            status_reason = "OUT_OF_PACK_GEOGRAPHY"
            coverage_tier = "UNDER_REVIEW"
            # Hide non-FL research seed from Covered checklist response; HOA assistive OK
            municipal_code = None
            checklist = []
            if hoa_rule:
                checklist.append({
                    "task_name": f"HOA Registration: {hoa_rule.hoa_name}",
                    "status": "PENDING",
                    "is_compliant": False,
                    "source_url": hoa_rule.official_website or None,
                })
        elif getattr(municipal_code, "is_ai_scraped", False):
            status_reason = "THIN_COVERAGE"
            coverage_tier = "THIN"
            municipal_code = None
            checklist = []
        else:
            status_reason = "MISSING_MUNICIPAL_CODE"
            coverage_tier = "UNDER_REVIEW"
    else:
        coverage_tier = "CURATED"

    if is_under_review:
        is_compliant = False

    status_label = "UNDER_REVIEW" if is_under_review else ("RESTRICTED" if not is_compliant else "ALLOWED_WITH_CHECKLIST")

    # SP-011: enqueue internal research on miss (fire-and-forget; never blocks / never auto-Covered)
    if is_under_review and (city or county):
        try:
            from app.services.research_queue import enqueue_research
            muni_name = city or (county.replace(" County", "").strip() if county else None)
            jt = "city" if city else "county"
            reason = status_reason or "MISSING_MUNICIPAL_CODE"
            enqueue_research(
                db,
                state=state_upper or "ZZ",
                municipality_name=muni_name or "unknown",
                jurisdiction_type=jt,
                sample_address=address,
                trigger_reason=reason,
            )
        except Exception:
            pass

    return AddressComplianceResponse(
        address=address,
        is_compliant=is_compliant,
        is_under_review=is_under_review,
        status=status_label,
        status_reason=status_reason,
        coverage_tier=coverage_tier,
        municipal_code=municipal_code,
        hoa_rule=hoa_rule,
        checklist=checklist
    )


@router.get("/tasks/{task_id}")
def get_compliance_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    from app.models.compliance import PropertyCompliance, MunicipalCode
    from app.models.property import Property
    from app.models.host import Host
    from app.core.billing_gate import require_active_essentials
    import uuid

    try:
        host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    except Exception:
        host = None
    # US-006: Tier 1 task depth — 403 when Free (never 500)
    require_active_essentials(db, host)

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
        "verification_notes": task.verification_notes,
        "source_url": (m_code.source_url if m_code and m_code.source_url else None),
    }


from fastapi import UploadFile, File
import shutil
import os

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks, status

def recalculate_property_compliance_score(property_id: str, db: Session) -> float:
    from app.models.compliance import PropertyCompliance
    tasks = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == property_id).all()
    if not tasks:
        return 100.0
    compliant_count = sum(1 for t in tasks if t.is_compliant and t.status == "APPROVED")
    return round((compliant_count / len(tasks)) * 100.0, 1)


@router.get("/documents/{filename}/download")
def download_private_document(
    filename: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    from fastapi.responses import FileResponse
    # BUG-008: require auth — unauthenticated downloads forbidden
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    # US-006: gated docs require active Essentials
    from app.models.host import Host
    from app.core.billing_gate import require_active_essentials
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    require_active_essentials(db, host)
    safe_filename = os.path.basename(filename)
    candidates = [
        os.path.join("app/storage/private_uploads", safe_filename),
        os.path.join("app/static/uploaded_permits", safe_filename),
        os.path.join("app/static/uploaded_hoa", safe_filename)
    ]
    
    target_path = None
    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            target_path = cand
            break
            
    if not target_path:
        raise HTTPException(status_code=404, detail="Document file not found")
        
    media_type = "application/pdf"
    if safe_filename.endswith(".png"):
        media_type = "image/png"
    elif safe_filename.endswith(".jpg") or safe_filename.endswith(".jpeg"):
        media_type = "image/jpeg"
        
    return FileResponse(target_path, media_type=media_type, filename=safe_filename)


@router.post("/tasks/{task_id}/upload")
def upload_compliance_task_file(
    task_id: str,
    background_tasks: BackgroundTasks,
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
        
    # Private storage directory for PII security
    upload_dir = "app/storage/private_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file safely in private storage
    raw_filename = os.path.basename(file.filename or "document.jpg")
    safe_filename = f"{task_id}_{raw_filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    file.file.seek(0)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Expose only via authenticated download route
    task.uploaded_file_url = f"/api/v1/compliance/documents/{safe_filename}/download"
    task.status = "PENDING"
    task.is_compliant = False
    task.verification_notes = "AI document auditing is in progress..."
    db.commit()
    
    # Dispatch document OCR processing asynchronously
    from app.tasks.audit import process_document_ocr
    background_tasks.add_task(process_document_ocr, str(task.id), task.uploaded_file_url)
    
    score = recalculate_property_compliance_score(task.property_id, db)

    return {
        "status": task.status or "PENDING",
        "uploaded_file_url": task.uploaded_file_url,
        "compliance_score": score,
        "message": "File uploaded successfully to secure storage. Document audit started."
    }


def call_gemini_hoa_ocr(file_bytes: bytes, mime_type: str, property_address: str = "") -> dict:
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_AI_KEY")
        or os.getenv("GOOGLE_MAPS_API_KEY")
        or os.getenv("Maps_API_KEY")
    )
    
    def _local_fallback():
        text_content = ""
        try:
            from io import BytesIO
            from app.services.ocr_service import extract_text_from_file_stream
            text_content = extract_text_from_file_stream(BytesIO(file_bytes))
        except Exception:
            try:
                text_content = file_bytes.decode("utf-8", errors="ignore")
            except Exception:
                pass
                
        lower_text = text_content.lower()
        str_permitted = "Yes"
        min_stay = "None"
        hoa_name = "Subdivision HOA"
        notes = "Extracted using local OCR compliance document engine."
        
        if "prohibit" in lower_text or "not allowed" in lower_text or "no short term" in lower_text or "no str" in lower_text or "no rentals" in lower_text:
            str_permitted = "No"
            notes = "HOA bylaws explicitly prohibit short-term rentals."
        elif "30 days" in lower_text or "monthly" in lower_text or "minimum 30" in lower_text:
            str_permitted = "No"
            min_stay = "30 days"
            notes = "HOA bylaws restrict rentals to minimum 30-day stays."
        elif "registered" in lower_text or "permit" in lower_text:
            notes = "HOA permits short-term rentals with mandatory registration."
            
        name_match = re.search(r'([A-Z][a-zA-Z0-9\s]+(?:HOA|Homeowners Association|Condominium Association|Community))', text_content)
        if name_match:
            hoa_name = name_match.group(1).strip()
            
        return {
            "hoa_name": hoa_name,
            "str_permitted": str_permitted,
            "minimum_lease_stay": min_stay,
            "key_rules_notes": notes,
            "is_valid": True
        }

    if api_key:
        try:
            b64_data = base64.b64encode(file_bytes).decode("utf-8")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            
            prompt = (
                "You are an HOA and real estate compliance auditor. Analyze the attached document "
                "(CC&Rs, HOA bylaws, or lease rules) and extract key rental restrictions in valid JSON format:\n"
                "{\n"
                "  \"hoa_name\": \"Extracted HOA or Community Name\",\n"
                "  \"str_permitted\": \"Yes\" or \"No\",\n"
                "  \"minimum_lease_stay\": \"e.g. 30 days, 7 days, 14 days, or None\",\n"
                "  \"key_rules_notes\": \"Detailed summary of short term rental rules, prohibitions, guest limits, or permit registration requirement.\"\n"
                "}\n"
                "Do not include markdown code block formatting."
            )
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": b64_data
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                if raw_text.startswith("```json"):
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()
                return json.loads(raw_text)
        except Exception as e:
            logging.error(f"Gemini HOA extraction error: {e}")

    return _local_fallback()


@router.post("/hoa/upload")
def upload_hoa_document(
    property_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/compliance/hoa/upload
    Accepts property_id and an uploaded HOA document (PDF/Image/Text).
    Stores file securely in private_uploads and uses Gemini 1.5 Pro AI to extract HOA rules,
    updating HOARule records and property compliance score dynamically.
    """
    from app.models.property import Property
    from app.models.compliance import PropertyCompliance, HOARule
    from datetime import date
    import base64
    import requests
    import logging

    property_item = db.query(Property).filter(Property.id == property_id).first()
    if not property_item:
        raise HTTPException(status_code=404, detail="Property not found")

    upload_dir = "app/storage/private_uploads"
    os.makedirs(upload_dir, exist_ok=True)

    raw_filename = os.path.basename(file.filename or "hoa_document.pdf")
    safe_filename = f"{property_id}_{raw_filename}"
    file_path = os.path.join(upload_dir, safe_filename)

    file.file.seek(0)
    file_bytes = file.file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    mime_type = file.content_type or "application/pdf"
    if safe_filename.endswith(".png"):
        mime_type = "image/png"
    elif safe_filename.endswith(".jpg") or safe_filename.endswith(".jpeg"):
        mime_type = "image/jpeg"

    # Call Gemini HOA extraction
    hoa_info = call_gemini_hoa_ocr(file_bytes, mime_type, property_item.address)
    
    # Clean up file_bytes stream from memory immediately after extraction
    del file_bytes

    hoa_name = hoa_info.get("hoa_name") or "Community HOA"
    str_permitted = hoa_info.get("str_permitted") or "Yes"
    minimum_lease_stay = hoa_info.get("minimum_lease_stay") or "None"
    key_rules_notes = hoa_info.get("key_rules_notes") or "HOA rules extracted via AI scanner."

    loc = property_item.city or property_item.address or "Florida"
    hoa_rule = db.query(HOARule).filter(HOARule.location.ilike(f"%{loc}%")).first()
    if not hoa_rule:
        hoa_rule = HOARule(
            hoa_name=hoa_name,
            location=loc,
            str_permitted=str_permitted,
            minimum_lease_stay=minimum_lease_stay,
            rules_available=True,
            key_rules_notes=key_rules_notes,
            last_confirmed_date=date.today()
        )
        db.add(hoa_rule)
    else:
        hoa_rule.hoa_name = hoa_name
        hoa_rule.str_permitted = str_permitted
        hoa_rule.minimum_lease_stay = minimum_lease_stay
        hoa_rule.rules_available = True
        hoa_rule.key_rules_notes = key_rules_notes
        hoa_rule.last_confirmed_date = date.today()

    # Update Property status
    is_allowed = str_permitted.strip().lower() == "yes"
    property_item.zoning_status = "Compliant" if is_allowed else "Violation"
    property_item.hoa_status = True

    # Expose file only through authenticated download URL
    file_download_url = f"/api/v1/compliance/documents/{safe_filename}/download"

    # Update matching compliance tasks for this property
    tasks = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == property_id).all()
    for t in tasks:
        if t.task_name and "HOA" in t.task_name.upper():
            t.status = "APPROVED" if is_allowed else "REJECTED"
            t.is_compliant = is_allowed
            t.uploaded_file_url = file_download_url
            t.verification_notes = f"AI HOA Audit: {key_rules_notes}"
            t.ocr_metadata_json = json.dumps(hoa_info)

    db.commit()
    
    # Recalculate dynamic property compliance score
    new_compliance_score = recalculate_property_compliance_score(property_id, db)

    return {
        "status": "APPROVED" if is_allowed else "REJECTED",
        "property_id": property_id,
        "hoa_name": hoa_name,
        "str_permitted": str_permitted,
        "minimum_lease_stay": minimum_lease_stay,
        "key_rules_notes": key_rules_notes,
        "uploaded_file_url": file_download_url,
        "compliance_score": new_compliance_score,
        "zoning_status": property_item.zoning_status,
        "message": f"HOA Document uploaded & scanned. Property status updated to {property_item.zoning_status}."
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
        # SP-002 / BUG-010: real host data or honest N/A — never invent parcel ids / owner names
        host_for_prefill = None
        try:
            from app.models.host import Host as _Host
            if getattr(prop, "user_id", None):
                host_for_prefill = db.query(_Host).filter(_Host.id == prop.user_id).first()
        except Exception:
            host_for_prefill = None
        owner = None
        if host_for_prefill is not None:
            owner = getattr(host_for_prefill, "username", None) or getattr(host_for_prefill, "email", None)
        prefill_data = {
            "owner_name": owner or "Unknown Host",
            "property_address": prop.address,
            "city": prop.city,
            "state": prop.state,
            "zip_code": prop.zip_code,
            "parcel_id": getattr(prop, "parcel_id", None) or "N/A",
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
        
    host_name = getattr(host_obj, "owner_name", None) or host_obj.username or "Unknown Host"
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


