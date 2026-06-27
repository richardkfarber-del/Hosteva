from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import secrets
from icalendar import Calendar, Event

from app.database import get_db
from app.models.property import Property
from app.db_models import Reservation
from app.tasks.calendar import sync_ical_calendars

router = APIRouter(
    prefix="/api/v1/operations",
    tags=["operations"]
)

class SyncIcalRequest(BaseModel):
    property_id: str
    airbnb_ical_import_url: Optional[str] = None
    vrbo_ical_import_url: Optional[str] = None

@router.post("/sync-ical")
def sync_ical_feeds(
    payload: SyncIcalRequest,
    db: Session = Depends(get_db)
):
    # 1. Fetch property
    prop = db.query(Property).filter(Property.id == payload.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # 2. Update import URLs
    if payload.airbnb_ical_import_url is not None:
        prop.airbnb_ical_import_url = payload.airbnb_ical_import_url
    if payload.vrbo_ical_import_url is not None:
        prop.vrbo_ical_import_url = payload.vrbo_ical_import_url

    # 3. Ensure export token exists
    if not prop.hosteva_ical_export_token:
        prop.hosteva_ical_export_token = f"hev_{secrets.token_hex(16)}"

    db.commit()
    db.refresh(prop)

    # 4. Trigger Celery sync task asynchronously
    sync_ical_calendars.delay(prop.id)

    return {
        "status": "success",
        "airbnb_ical_import_url": prop.airbnb_ical_import_url,
        "vrbo_ical_import_url": prop.vrbo_ical_import_url,
        "hosteva_ical_export_token": prop.hosteva_ical_export_token,
        "hosteva_ical_export_url": f"/api/v1/operations/calendar/export?token={prop.hosteva_ical_export_token}"
    }

@router.get("/calendar/export")
def export_calendar(
    token: str,
    db: Session = Depends(get_db)
):
    if not token or not token.strip():
        raise HTTPException(status_code=401, detail="Token parameter is required.")

    # 1. Fetch property by export token
    prop = db.query(Property).filter(Property.hosteva_ical_export_token == token).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Invalid token or property not found.")

    # 2. Fetch all reservations
    reservations = db.query(Reservation).filter(Reservation.property_id == prop.id).all()

    # 3. Construct iCal Calendar payload
    cal = Calendar()
    cal.add("prodid", "-//Hosteva Sync Engine//hosteva.com//")
    cal.add("version", "2.0")

    for res in reservations:
        event = Event()
        event.add("summary", res.guest_name or f"Reserved Block ({res.ota_source})")
        event.add("dtstart", res.check_in)
        event.add("dtend", res.check_out)
        event.add("uid", res.external_booking_id)
        cal.add_component(event)

    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=hosteva_calendar_{prop.id}.ics"
        }
    )
