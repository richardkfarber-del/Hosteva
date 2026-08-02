from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from pydantic import BaseModel
from app.database import get_db
import sys
import os
import requests
import urllib.parse
import json
from app.services.compliance import run_gemini_audit
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.email_service import dispatch_email_alert
from app.models.property import Property
from app.models.host import Host
from app.core.security import get_current_user

router = APIRouter(prefix="/api/properties", tags=["Properties"])


def fetch_real_property_image(address: str) -> str:
    import logging
    logger = logging.getLogger("app.routers.properties")
    logger.info(f"DEBUG: fetch_real_property_image starting for address: {address}")
    print(f"DEBUG: fetch_real_property_image starting for address: {address}", flush=True)
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("Maps_API_KEY")
    fallback_url = "/static/img/fallback_house.jpg"
    if not api_key:
        print("DEBUG: Google Street View Onboarding: GOOGLE_MAPS_API_KEY or Maps_API_KEY is not configured.", flush=True)
        logger.warning("DEBUG: Google Street View Onboarding: GOOGLE_MAPS_API_KEY or Maps_API_KEY is not configured.")
        return fallback_url
    
    print(f"DEBUG: Google Street View Onboarding: Fetching image for address: {address}", flush=True)
    logger.info(f"DEBUG: Google Street View Onboarding: Fetching image for address: {address}")
    
    import uuid
    # 1. Try Google Street View metadata first to check availability
    try:
        metadata_url = "https://maps.googleapis.com/maps/api/streetview/metadata"
        params = {
            "location": address,
            "key": api_key
        }
        resp = requests.get(metadata_url, params=params, timeout=5)
        status_code = resp.status_code
        print(f"DEBUG: Image fetch status for {address}: {status_code}", flush=True)
        logger.info(f"DEBUG: Image fetch status for {address}: {status_code}")
        print(f"DEBUG: Google Street View API Metadata response text: {resp.text}", flush=True)
        logger.info(f"DEBUG: Google Street View API Metadata response text: {resp.text}")
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status")
            print(f"DEBUG: Google Street View API Metadata status field: {status}", flush=True)
            logger.info(f"DEBUG: Google Street View API Metadata status field: {status}")
            if status == "OK":
                escaped_addr = urllib.parse.quote(address)
                street_view_url = f"https://maps.googleapis.com/maps/api/streetview?size=800x600&location={escaped_addr}&key={api_key}"
                print("DEBUG: Google Street View Onboarding: Successfully resolved Street View metadata. Downloading image server-side...", flush=True)
                logger.info("DEBUG: Google Street View Onboarding: Successfully resolved Street View metadata. Downloading image server-side...")
                img_resp = requests.get(street_view_url, timeout=10)
                if img_resp.status_code == 200:
                    img_uuid = str(uuid.uuid4())
                    os.makedirs("app/static/property_images", exist_ok=True)
                    file_path = f"app/static/property_images/{img_uuid}.jpg"
                    with open(file_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"DEBUG: Real image successfully saved to {file_path}", flush=True)
                    logger.info(f"DEBUG: Real image successfully saved to {file_path}")
                    print("DEBUG: Success! Image retrieved using New Key via Street View API.", flush=True)
                    logger.info("DEBUG: Success! Image retrieved using New Key via Street View API.")
                    return f"/static/property_images/{img_uuid}.jpg"
    except Exception as e:
        print(f"DEBUG: Error checking Street View metadata: {e}", flush=True)
        logger.exception("DEBUG: Error checking Street View metadata")
        
    # 2. Try Google Places API to find a photo if Street View is not available
    try:
        find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": address,
            "inputtype": "textquery",
            "fields": "photos",
            "key": api_key
        }
        resp = requests.get(find_place_url, params=params, timeout=5)
        print(f"DEBUG: Google Places API Find Place response code: {resp.status_code}", flush=True)
        logger.info(f"DEBUG: Google Places API Find Place response code: {resp.status_code}")
        print(f"DEBUG: Google Places API Find Place response text: {resp.text}", flush=True)
        logger.info(f"DEBUG: Google Places API Find Place response text: {resp.text}")
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            print(f"DEBUG: Google Places API Find Place candidates count: {len(candidates)}", flush=True)
            logger.info(f"DEBUG: Google Places API Find Place candidates count: {len(candidates)}")
            if candidates:
                photos = candidates[0].get("photos", [])
                print(f"DEBUG: Google Places API Find Place photos count: {len(photos)}", flush=True)
                logger.info(f"DEBUG: Google Places API Find Place photos count: {len(photos)}")
                if photos:
                    photo_ref = photos[0].get("photo_reference")
                    places_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_ref}&key={api_key}"
                    print("DEBUG: Google Street View Onboarding: Successfully resolved Places photo. Downloading image server-side...", flush=True)
                    logger.info("DEBUG: Google Street View Onboarding: Successfully resolved Places photo. Downloading image server-side...")
                    img_resp = requests.get(places_url, timeout=10)
                    if img_resp.status_code == 200:
                        img_uuid = str(uuid.uuid4())
                        os.makedirs("app/static/property_images", exist_ok=True)
                        file_path = f"app/static/property_images/{img_uuid}.jpg"
                        with open(file_path, "wb") as f:
                            f.write(img_resp.content)
                        print(f"DEBUG: Real image successfully saved to {file_path}", flush=True)
                        logger.info(f"DEBUG: Real image successfully saved to {file_path}")
                        print("DEBUG: Success! Image retrieved using New Key via Places API.", flush=True)
                        logger.info("DEBUG: Success! Image retrieved using New Key via Places API.")
                        return f"/static/property_images/{img_uuid}.jpg"
    except Exception as e:
        print(f"DEBUG: Error checking Places API photo: {e}", flush=True)
        logger.exception("DEBUG: Error checking Places API photo")
        
    print("DEBUG: Google Street View Onboarding: No real image found. Falling back to default property image.", flush=True)
    logger.info("DEBUG: Google Street View Onboarding: No real image found. Falling back to default property image.")
    return fallback_url


def geocode_address(address: str) -> dict:
    """
    Geocodes an address to identify locality (City), administrative_area_level_2 (County),
    and administrative_area_level_1 (State), and raw address components.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("Maps_API_KEY")
    if not api_key:
        print("Geocoding address WARNING: GOOGLE_MAPS_API_KEY or Maps_API_KEY is not configured.")
        return {"city": "", "county": "", "state": "", "address_components": []}
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": api_key}
        resp = requests.get(url, params=params, timeout=5)
        print(f"Geocoding API response code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Geocoding API status: {data.get('status')}")
            if data.get("status") == "OK" and data.get("results"):
                components = data["results"][0].get("address_components", [])
                city = ""
                county = ""
                state = ""
                for c in components:
                    types = c.get("types", [])
                    if "locality" in types:
                        city = c.get("long_name", "")
                    elif "administrative_area_level_2" in types:
                        county = c.get("long_name", "")
                    elif "administrative_area_level_1" in types:
                        state = c.get("short_name", "")
                print(f"Geocoded result: city='{city}', county='{county}', state='{state}'")
                return {"city": city, "county": county, "state": state, "address_components": components}
    except Exception as e:
        print(f"Error geocoding address: {e}")
    return {"city": "", "county": "", "state": "", "address_components": []}


class PropertyCreate(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str = ""
    property_type: str = ""
    hoa_status: bool = False


@router.get("/", response_model=List[Dict[str, Any]])
def get_properties(
    status: str = Query(None, description="Filter by zoning status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import logging
    logger = logging.getLogger("app.routers.properties")
    
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    query = db.query(Property).filter(Property.user_id == host.id)
    properties = query.all()
    
    # Self-healing checklist seeding for properties
    from app.models.compliance import PropertyCompliance, MunicipalCode
    import uuid
    
    for p in properties:
        if p.required_permits:
            try:
                tasks = json.loads(p.required_permits)
            except:
                tasks = []
            if tasks:
                existing_count = db.query(PropertyCompliance).filter(PropertyCompliance.property_id == p.id).count()
                if existing_count < len(tasks):
                    # Seed missing checklist rows
                    state_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%State of Florida%")).first()
                    if not state_code:
                        state_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%Florida%")).first()
                    if not state_code:
                        state_code = db.query(MunicipalCode).first()
                    
                    fallback_mc_id = state_code.id if state_code else None
                    if not fallback_mc_id:
                        fallback_mc_id = uuid.uuid4()
                        
                    hillsborough_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%Hillsborough County%")).first()
                    st_pete_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%St. Petersburg%")).first()
                    pasco_code = db.query(MunicipalCode).filter(MunicipalCode.municipality_name.ilike("%Pasco County%")).first()
                    
                    state_id = state_code.id if state_code else fallback_mc_id
                    hillsborough_id = hillsborough_code.id if hillsborough_code else (state_id or fallback_mc_id)
                    st_pete_id = st_pete_code.id if st_pete_code else (state_id or fallback_mc_id)
                    pasco_id = pasco_code.id if pasco_code else (state_id or fallback_mc_id)
                    
                    valid_period = '[2026-06-04 00:00:00, 2027-06-04 00:00:00]'
                    
                    for task_name in tasks:
                        exists = db.query(PropertyCompliance).filter(
                            PropertyCompliance.property_id == p.id,
                            PropertyCompliance.violation_notes == task_name
                        ).first()
                        if not exists:
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
                                property_id=p.id,
                                municipal_code_id=mc_id,
                                is_compliant=False,
                                status="PENDING",
                                verification_notes=None,
                                task_name=task_name,
                                violation_notes=task_name,
                                valid_period=valid_period
                            )
                            db.add(item)
                    db.commit()
    
    if not properties:
        sql_query = "Unknown"
        try:
            sql_query = str(query.statement.compile(dialect=db.bind.dialect, compile_kwargs={"literal_binds": True}))
        except Exception:
            try:
                sql_query = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
            except Exception:
                sql_query = str(query)
        logger.info(f"DEBUG: Empty dashboard. Executed SQL query: {sql_query}")
        print(f"DEBUG: Empty dashboard. Executed SQL query: {sql_query}", flush=True)
        
    result = [
        {
            "id": p.id,
            "address": p.address or "Unknown Address",
            "location": f"{p.city or ''}, {p.state or ''}".strip(", "),
            "zoning_status": p.zoning_status or "Pending",
            "beds": 3,
            "baths": 2,
            "price": 149 if p.property_type and p.property_type.lower() == "condo" else 249,
            "image_url": p.image_url or "",
            "required_permits": json.loads(p.required_permits) if p.required_permits else [],
            "local_restrictions": json.loads(p.local_restrictions) if p.local_restrictions else {},
            "lat": 34.0901,
            "lng": -118.3617
        }
        for p in properties
    ]
    if status:
        result = [p for p in result if p["zoning_status"] and p["zoning_status"].lower() == status.lower()]
    return result


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    # Fetch real property imagery
    full_address = f"{property_data.address}, {property_data.city}, {property_data.state} {property_data.zip_code}".strip()
    image_url = fetch_real_property_image(full_address)

    # Jurisdiction-Aware Geocoding (extract City and County)
    geocoded = geocode_address(full_address)
    city_name = geocoded.get("city") or property_data.city
    county_name = geocoded.get("county") or (f"{city_name} County" if city_name else "Unknown County")
    state_name = geocoded.get("state") or property_data.state

    # Execute Gemini Compliance Audit
    audit_results = run_gemini_audit(
        city=city_name,
        county=county_name,
        state=state_name,
        address=full_address,
        address_components=geocoded.get("address_components")
    )

    db_property = Property(
        user_id=host.id,
        address=property_data.address,
        city=city_name,
        state=state_name,
        zip_code=property_data.zip_code,
        property_type=property_data.property_type,
        hoa_status=audit_results.get("hoa_detected", False),
        zoning_status=audit_results.get("eligibility_status", "Pending"),
        image_url=image_url,
        required_permits=json.dumps(audit_results.get("required_permits", [])),
        local_restrictions=json.dumps(audit_results.get("local_restrictions", {}))
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)

    # Seed checklist items in property_compliance
    import uuid
    from app.models.compliance import PropertyCompliance, MunicipalCode
    from app.tasks.scraper import run_agent_compliance_scraper
    
    # 1. Look up matched municipal code
    municipal_code = None
    if city_name:
        municipal_code = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike(city_name),
            MunicipalCode.jurisdiction_type.ilike("City"),
            MunicipalCode.state.ilike(state_name)
        ).first()
        
    if not municipal_code and county_name:
        clean_county = county_name.replace(" County", "").strip()
        municipal_code = db.query(MunicipalCode).filter(
            (MunicipalCode.municipality_name.ilike(county_name)) | 
            (MunicipalCode.municipality_name.ilike(clean_county)),
            MunicipalCode.jurisdiction_type.ilike("County"),
            MunicipalCode.state.ilike(state_name)
        ).first()
        
    valid_period = '[2026-06-04 00:00:00, 2027-06-04 00:00:00]'
    
    if municipal_code:
        # Match found! Use pre-compiled rules
        tasks = []
        if municipal_code.requires_permit:
            tasks.append(f"{city_name} Short-Term Rental Permit")
        if municipal_code.tax_rate_registration_fee and ("tax" in municipal_code.tax_rate_registration_fee.lower() or municipal_code.tax_rate):
            tasks.append(f"{state_name} Transient Occupancy Tax Registration")
            
        # Add Florida defaults if FL
        if state_name.upper() == "FL":
            if "DBPR Vacation Rental License" not in tasks:
                tasks.append("DBPR Vacation Rental License")
            if "Florida Dept of Revenue Sales Tax Registration" not in tasks:
                tasks.append("Florida Dept of Revenue Sales Tax Registration")
            if "County Tourist Development Tax Account" not in tasks:
                tasks.append("County Tourist Development Tax Account")
                
        # If tasks list is still empty, default to required permits from audit results
        if not tasks:
            try:
                tasks = json.loads(db_property.required_permits) if db_property.required_permits else []
            except:
                tasks = []
                
        if not tasks:
            tasks = ["DBPR Vacation Rental License", "Florida Dept of Revenue Sales Tax Registration", "County Tourist Development Tax Account"]
            
        for task_name in tasks:
            item = PropertyCompliance(
                property_id=db_property.id,
                municipal_code_id=municipal_code.id,
                is_compliant=False,
                status="NOT_UPLOADED",
                verification_notes=None,
                task_name=task_name,
                violation_notes=task_name,
                valid_period=valid_period
            )
            db.add(item)
        db.commit()
    else:
        # Cache miss! Create temporary MunicipalCode record and trigger Real-time AI Scraper
        temp_mc = MunicipalCode(
            municipality_name=city_name,
            jurisdiction_type="City" if city_name else "County",
            ordinance_number="PENDING-SCRAPE",
            str_prohibited=False,
            is_allowed=True,
            requires_permit=True,
            state=state_name,
            is_ai_scraped=True,
            is_expert_verified=False
        )
        db.add(temp_mc)
        db.commit()
        db.refresh(temp_mc)
        
        # Create temporary check task
        task_name = "Zoning Rules Under Manual Curation"
        item = PropertyCompliance(
            property_id=db_property.id,
            municipal_code_id=temp_mc.id,
            is_compliant=False,
            status="PENDING_REVIEW",  # Triggers Rules Under Manual Review indicator
            task_name=task_name,
            violation_notes="System enqueued for manual curator review.",
            valid_period=valid_period
        )
        db.add(item)
        db.commit()
        
        # Trigger scraper Celery task
        db_property.zoning_status = "Pending"
        db.commit()
        run_agent_compliance_scraper.delay(
            str(db_property.id),
            city_name,
            county_name,
            state_name
        )

    return {
        "id": db_property.id,
        "address": db_property.address,
        "location": f"{db_property.city}, {db_property.state}",
        "zoning_status": db_property.zoning_status,
        "beds": 3,
        "baths": 2,
        "price": 249,
        "image_url": db_property.image_url or "",
        "required_permits": json.loads(db_property.required_permits) if db_property.required_permits else [],
        "local_restrictions": json.loads(db_property.local_restrictions) if db_property.local_restrictions else {}
    }


@router.post("/{property_id}/evaluate")
def evaluate_compliance(
    property_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    property_item = db.query(Property).filter(Property.id == property_id, Property.user_id == host.id).first()
    if not property_item:
        raise HTTPException(status_code=404, detail="Property not found")
        
    old_status = property_item.zoning_status
    new_status = "Compliant"
    
    # Simple logic
    property_item.zoning_status = new_status
    db.commit()
    
    if new_status == "Violation":
        dispatch_email_alert(host.email, property_id, old_status, new_status)
        
    return {"message": "Property evaluated", "status": new_status}


@router.post("/{property_id}/upload-vision")
def upload_vision(
    property_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Drag-and-drop file upload endpoint that accepts photos of property rooms,
    sends them to the Gemini 1.5 Pro model for analysis, and returns the results.
    """
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host profile not found")
        
    property_item = db.query(Property).filter(Property.id == property_id, Property.user_id == host.id).first()
    if not property_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
        
    try:
        from app.services.compliance import run_gemini_vision
        contents = file.file.read()
        mime_type = file.content_type or "image/jpeg"
        
        # Analyze the photo using Gemini 1.5 Pro Vision
        result = run_gemini_vision(contents, mime_type)
        return result
    except Exception as e:
        print(f"DEBUG: Vision upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{property_id}/upload-hoa")
def upload_hoa_for_property(
    property_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    POST /api/properties/{property_id}/upload-hoa
    Accepts an uploaded HOA document for a property and runs AI rules extraction.
    """
    from app.api.v1.compliance import upload_hoa_document
    class FormWrapper:
        pass
    return upload_hoa_document(property_id=property_id, file=file, db=db)

