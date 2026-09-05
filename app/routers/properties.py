from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from pydantic import BaseModel
from app.database import get_db
import sys
import os
import logging
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


FALLBACK_PROPERTY_IMAGE_URL = "/static/img/fallback_house.jpg"
logger = logging.getLogger("app.routers.properties")


def _empty_geocode_result() -> dict:
    return {
        "city": "",
        "county": "",
        "state": "",
        "address_components": [],
        "formatted_address": "",
        "lat": None,
        "lng": None,
    }


def _as_location_str(value) -> str:
    """Coerce geocode/SV location fields to str so retry never TypeErrors."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _fallback_audit_results(city: str) -> dict:
    return {
        "legal_subdivision_name": city or "Unknown Subdivision",
        "hoa_detected": False,
        "hoa_rules_available": False,
        "eligibility_status": "Pending",
        "required_permits": [
            "Manual review required: automated compliance audit unavailable",
            "DBPR Condominium/Cooperative/Apartment License",
            "Florida Dept of Revenue Sales Tax Registration",
            "County Tourist Development Tax Account",
        ],
        "local_restrictions": {
            "disclaimer": (
                "Hosteva automated compliance results are informational only "
                "and do not constitute legal advice."
            ),
        },
    }


def is_fallback_property_image(url: str | None) -> bool:
    """True when image_url is missing or the stock placeholder (not a real facade)."""
    if not url:
        return True
    return "fallback_house.jpg" in url


def _save_property_image_bytes(content: bytes) -> str:
    import uuid
    img_uuid = str(uuid.uuid4())
    os.makedirs("app/static/property_images", exist_ok=True)
    file_path = f"app/static/property_images/{img_uuid}.jpg"
    with open(file_path, "wb") as f:
        f.write(content)
    return f"/static/property_images/{img_uuid}.jpg"


def _try_street_view_image(location: str, api_key: str, logger) -> str | None:
    """Return saved /static/property_images/*.jpg if Street View metadata is OK for location."""
    if not location:
        return None
    try:
        metadata_url = "https://maps.googleapis.com/maps/api/streetview/metadata"
        params = {"location": location, "key": api_key}
        resp = requests.get(metadata_url, params=params, timeout=5)
        print(f"DEBUG: Street View metadata for {location!r}: HTTP {resp.status_code} body={resp.text}", flush=True)
        logger.info("DEBUG: Street View metadata for %r: HTTP %s body=%s", location, resp.status_code, resp.text)
        if resp.status_code != 200:
            return None
        data = resp.json()
        status = data.get("status")
        if status != "OK":
            print(f"DEBUG: Street View metadata status={status} for {location!r} — not short-circuiting callers; retry paths may continue.", flush=True)
            logger.info("DEBUG: Street View metadata status=%s for %r", status, location)
            return None
        img_resp = requests.get(
            "https://maps.googleapis.com/maps/api/streetview",
            params={"size": "800x600", "location": location, "key": api_key},
            timeout=10,
        )
        if img_resp.status_code == 200 and img_resp.content:
            saved = _save_property_image_bytes(img_resp.content)
            print(f"DEBUG: Street View image saved to {saved} for location={location!r}", flush=True)
            logger.info("DEBUG: Street View image saved to %s for location=%r", saved, location)
            return saved
    except Exception:
        print(f"DEBUG: Error checking Street View for {location!r}", flush=True)
        logger.exception("DEBUG: Error checking Street View for %r", location)
    return None


def _try_places_photo(query: str, api_key: str, logger) -> str | None:
    """Return saved Places photo path if Find Place yields a photo for query."""
    if not query:
        return None
    try:
        find_place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": query,
            "inputtype": "textquery",
            "fields": "photos",
            "key": api_key,
        }
        resp = requests.get(find_place_url, params=params, timeout=5)
        print(f"DEBUG: Places Find Place for {query!r}: HTTP {resp.status_code} body={resp.text}", flush=True)
        logger.info("DEBUG: Places Find Place for %r: HTTP %s body=%s", query, resp.status_code, resp.text)
        if resp.status_code != 200:
            return None
        candidates = resp.json().get("candidates", [])
        if not candidates:
            return None
        photos = candidates[0].get("photos") or []
        if not photos:
            return None
        photo_ref = photos[0].get("photo_reference")
        if not photo_ref:
            return None
        img_resp = requests.get(
            "https://maps.googleapis.com/maps/api/place/photo",
            params={"maxwidth": 800, "photo_reference": photo_ref, "key": api_key},
            timeout=10,
        )
        if img_resp.status_code == 200 and img_resp.content:
            saved = _save_property_image_bytes(img_resp.content)
            print(f"DEBUG: Places photo saved to {saved} for query={query!r}", flush=True)
            logger.info("DEBUG: Places photo saved to %s for query=%r", saved, query)
            return saved
    except Exception:
        print(f"DEBUG: Error checking Places photo for {query!r}", flush=True)
        logger.exception("DEBUG: Error checking Places photo for %r", query)
    return None


def fetch_real_property_image(address: str, geocoded: dict | None = None) -> str:
    """Prefer Street View / Places photo; geocode-normalize and retry before stock fallback.

    BUG-PL-02: a metadata miss on the raw address must not silent-stock without
    retrying geocode-normalized formatted_address and lat,lng.
    BUG-PL-07: never raise — always degrade to labeled placeholder.
    """
    try:
        return _fetch_real_property_image_inner(address, geocoded)
    except Exception:
        logger.exception("BUG-PL-07: fetch_real_property_image failed for %r; using placeholder", address)
        return FALLBACK_PROPERTY_IMAGE_URL


def _fetch_real_property_image_inner(address: str, geocoded: dict | None = None) -> str:
    logger.info("DEBUG: fetch_real_property_image starting for address: %s", address)
    print(f"DEBUG: fetch_real_property_image starting for address: {address}", flush=True)

    api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("Maps_API_KEY")
    if not api_key:
        print("DEBUG: Google Street View Onboarding: GOOGLE_MAPS_API_KEY or Maps_API_KEY is not configured.", flush=True)
        logger.warning("DEBUG: Google Street View Onboarding: GOOGLE_MAPS_API_KEY or Maps_API_KEY is not configured.")
        return FALLBACK_PROPERTY_IMAGE_URL

    # 1) Raw address — Street View then Places
    saved = _try_street_view_image(address, api_key, logger)
    if saved:
        return saved
    saved = _try_places_photo(address, api_key, logger)
    if saved:
        return saved

    # 2) Geocode-normalized retry (BUG-PL-02) — do not short-circuit to stock on first miss
    geo = geocoded if isinstance(geocoded, dict) else None
    if not geo or not (geo.get("formatted_address") or geo.get("lat") is not None):
        geo = geocode_address(address)
        if not isinstance(geo, dict):
            geo = _empty_geocode_result()

    formatted = _as_location_str((geo or {}).get("formatted_address"))
    lat = (geo or {}).get("lat")
    lng = (geo or {}).get("lng")
    latlng = f"{lat},{lng}" if lat is not None and lng is not None else ""

    addr_key = _as_location_str(address).strip().lower()
    tried = {addr_key} if addr_key else set()
    for loc in (formatted, latlng):
        if not loc:
            continue
        loc = _as_location_str(loc)
        key = loc.strip().lower()
        if key in tried:
            continue
        tried.add(key)
        print(f"DEBUG: Street View retry with geocode-normalized location={loc!r}", flush=True)
        logger.info("DEBUG: Street View retry with geocode-normalized location=%r", loc)
        saved = _try_street_view_image(loc, api_key, logger)
        if saved:
            return saved

    if formatted and formatted.strip().lower() not in tried:
        saved = _try_places_photo(formatted, api_key, logger)
        if saved:
            return saved

    print("DEBUG: Google Street View Onboarding: No real image found after geocode retry. Falling back to labeled placeholder.", flush=True)
    logger.info("DEBUG: Google Street View Onboarding: No real image found after geocode retry. Falling back to labeled placeholder.")
    return FALLBACK_PROPERTY_IMAGE_URL


def resolve_property_create_image(full_address: str, geocoded: dict | None = None) -> str:
    """Create-path image helper — never raises (BUG-PL-07)."""
    try:
        url = fetch_real_property_image(full_address, geocoded=geocoded)
        if url:
            return url
    except Exception:
        logger.exception("BUG-PL-07: resolve_property_create_image raised for %r", full_address)
    return FALLBACK_PROPERTY_IMAGE_URL


def geocode_address(address: str) -> dict:
    """
    Geocodes an address to identify locality (City), administrative_area_level_2 (County),
    and administrative_area_level_1 (State), plus formatted_address / lat / lng for image retry.
    """
    empty = _empty_geocode_result()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("Maps_API_KEY")
    if not api_key:
        print("Geocoding address WARNING: GOOGLE_MAPS_API_KEY or Maps_API_KEY is not configured.")
        return empty
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": api_key}
        resp = requests.get(url, params=params, timeout=5)
        print(f"Geocoding API response code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Geocoding API status: {data.get('status')}")
            if data.get("status") == "OK" and data.get("results"):
                result0 = data["results"][0]
                components = result0.get("address_components", [])
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
                loc = (result0.get("geometry") or {}).get("location") or {}
                formatted = _as_location_str(result0.get("formatted_address"))
                lat = loc.get("lat")
                lng = loc.get("lng")
                print(
                    f"Geocoded result: city='{city}', county='{county}', state='{state}', "
                    f"formatted={formatted!r}, lat={lat}, lng={lng}"
                )
                return {
                    "city": city,
                    "county": county,
                    "state": state,
                    "address_components": components,
                    "formatted_address": formatted,
                    "lat": lat,
                    "lng": lng,
                }
    except Exception as e:
        print(f"Error geocoding address: {e}")
    return empty


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
            "image_is_placeholder": is_fallback_property_image(p.image_url),
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


def _seed_create_checklist(db, db_property, city_name, county_name, state_name):
    """Best-effort checklist / scraper enqueue. Caller swallows failures (BUG-PL-07)."""
    from app.models.compliance import PropertyCompliance, MunicipalCode
    from app.tasks.scraper import run_agent_compliance_scraper

    # 1. Look up matched municipal code (retry without state if seed row has NULL state)
    municipal_code = None
    if city_name:
        municipal_code = db.query(MunicipalCode).filter(
            MunicipalCode.municipality_name.ilike(city_name),
            MunicipalCode.jurisdiction_type.ilike("City"),
            MunicipalCode.state.ilike(state_name)
        ).first()
        if not municipal_code:
            municipal_code = db.query(MunicipalCode).filter(
                MunicipalCode.municipality_name.ilike(city_name),
                MunicipalCode.jurisdiction_type.ilike("City"),
            ).first()
    
    if not municipal_code and county_name:
        clean_county = county_name.replace(" County", "").strip()
        municipal_code = db.query(MunicipalCode).filter(
            (MunicipalCode.municipality_name.ilike(county_name)) | 
            (MunicipalCode.municipality_name.ilike(clean_county)),
            MunicipalCode.jurisdiction_type.ilike("County"),
            MunicipalCode.state.ilike(state_name)
        ).first()
        if not municipal_code:
            municipal_code = db.query(MunicipalCode).filter(
                (MunicipalCode.municipality_name.ilike(county_name)) |
                (MunicipalCode.municipality_name.ilike(clean_county)),
                MunicipalCode.jurisdiction_type.ilike("County"),
            ).first()
    
    valid_period = '[2026-06-04 00:00:00, 2027-06-04 00:00:00]'

    if municipal_code:
        # Match found! Use pre-compiled rules
        tasks = []
        if municipal_code.requires_permit:
            tasks.append(f"{city_name} Short-Term Rental Permit")
        fee = municipal_code.tax_rate_registration_fee
        fee_l = fee.lower() if isinstance(fee, str) else ""
        if fee_l and ("tax" in fee_l or municipal_code.tax_rate):
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
    
        # Trigger scraper Celery task (must not 500 the HTTP create)
        db_property.zoning_status = "Pending"
        db.commit()
        try:
            run_agent_compliance_scraper.delay(
                str(db_property.id),
                city_name,
                county_name,
                state_name
            )
        except Exception:
            logger.exception("BUG-PL-07: scraper.delay failed for property %s", db_property.id)



@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")
        
    # Jurisdiction-Aware Geocoding first so Street View can retry normalized location (BUG-PL-02)
    # BUG-PL-07: geocode / image / audit must never 500 the create.
    full_address = f"{property_data.address}, {property_data.city}, {property_data.state} {property_data.zip_code}".strip()
    try:
        geocoded = geocode_address(full_address)
        if not isinstance(geocoded, dict):
            geocoded = _empty_geocode_result()
    except Exception:
        logger.exception("BUG-PL-07: geocode_address raised for %r", full_address)
        geocoded = _empty_geocode_result()
    image_url = resolve_property_create_image(full_address, geocoded=geocoded)
    city_name = geocoded.get("city") or property_data.city
    county_name = geocoded.get("county") or (f"{city_name} County" if city_name else "Unknown County")
    state_name = geocoded.get("state") or property_data.state

    # Execute Gemini Compliance Audit
    try:
        audit_results = run_gemini_audit(
            city=city_name,
            county=county_name,
            state=state_name,
            address=full_address,
            address_components=geocoded.get("address_components")
        )
        if not isinstance(audit_results, dict):
            audit_results = _fallback_audit_results(city_name)
    except Exception:
        logger.exception("BUG-PL-07: run_gemini_audit raised for %r", full_address)
        audit_results = _fallback_audit_results(city_name)

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

    def _create_payload(prop):
        return {
            "id": prop.id,
            "address": prop.address,
            "location": f"{prop.city}, {prop.state}",
            "zoning_status": prop.zoning_status,
            "beds": 3,
            "baths": 2,
            "price": 249,
            "image_url": prop.image_url or "",
            "image_is_placeholder": is_fallback_property_image(prop.image_url),
            "required_permits": json.loads(prop.required_permits) if prop.required_permits else [],
            "local_restrictions": json.loads(prop.local_restrictions) if prop.local_restrictions else {},
        }

    payload = _create_payload(db_property)

    # Seed checklist items in property_compliance (must not 500 after the row is saved)
    try:
        _seed_create_checklist(db, db_property, city_name, county_name, state_name)
        db.refresh(db_property)
        payload = _create_payload(db_property)
    except Exception:
        logger.exception(
            "BUG-PL-07: post-create municipal seed/scraper failed; property %s still returned",
            payload["id"],
        )
        try:
            db.rollback()
        except Exception:
            pass

    return payload


def _map_compliance_label_to_zoning(status_label: str) -> str:
    """Align property zoning_status with /api/v1/compliance truth (BUG-PL-05).

    Never maps to Compliant for Restricted / Pending / Under Review / checklist-required.
    """
    label = (status_label or "").strip().upper()
    if label == "RESTRICTED":
        return "Violation"
    if label in ("UNDER_REVIEW", "PENDING"):
        return "Pending"
    if label == "ALLOWED_WITH_CHECKLIST":
        # Allowed only after checklist — not a Compliant green light
        return "Action Required"
    if label == "COMPLIANT":
        # Evaluate must not invent Compliant from a bare label
        return "Action Required"
    return "Pending"


@router.post("/{property_id}/evaluate")
def evaluate_compliance(
    property_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Re-evaluate zoning against municipal compliance truth — never false Compliant."""
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")

    property_item = db.query(Property).filter(Property.id == property_id, Property.user_id == host.id).first()
    if not property_item:
        raise HTTPException(status_code=404, detail="Property not found")

    old_status = property_item.zoning_status
    full_address = ", ".join(
        p for p in [
            property_item.address,
            property_item.city,
            f"{property_item.state or ''} {property_item.zip_code or ''}".strip(),
        ] if p
    )

    compliance_status = "UNDER_REVIEW"
    try:
        from app.api.v1.compliance import get_compliance_by_address
        result = get_compliance_by_address(address=full_address, db=db)
        compliance_status = (
            getattr(result, "status", None)
            or (
                "UNDER_REVIEW" if getattr(result, "is_under_review", False)
                else ("RESTRICTED" if not getattr(result, "is_compliant", True) else "ALLOWED_WITH_CHECKLIST")
            )
        )
        new_status = _map_compliance_label_to_zoning(compliance_status)
    except Exception:
        # Fail closed: never invent Compliant when compliance lookup fails
        preserved = (old_status or "").strip()
        if preserved and preserved.lower() not in ("compliant", "green"):
            new_status = preserved
        else:
            new_status = "Pending"
        compliance_status = "LOOKUP_FAILED"

    # Hard guard: this endpoint must never claim Compliant
    if (new_status or "").strip().lower() == "compliant":
        new_status = "Action Required"

    property_item.zoning_status = new_status
    db.commit()

    if new_status == "Violation":
        dispatch_email_alert(host.email, property_id, old_status, new_status)

    return {
        "message": "Property evaluated",
        "status": new_status,
        "compliance_status": compliance_status,
        "previous_status": old_status,
    }


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

