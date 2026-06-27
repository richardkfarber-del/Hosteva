import os
import logging
import requests
from datetime import datetime, date
from icalendar import Calendar
from sqlalchemy.orm import Session

from app.tasks.config import celery_app
from app.database import SessionLocal
from app.models.property import Property
from app.db_models import Reservation

def normalize_to_date(dt) -> date:
    if isinstance(dt, datetime):
        return dt.date()
    elif isinstance(dt, date):
        return dt
    return dt

def fetch_and_parse_ical(url: str) -> list:
    if not url:
        return []
    try:
        # Fetch external feed
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            cal = Calendar.from_ical(resp.content)
            events = []
            for component in cal.walk():
                if component.name == "VEVENT":
                    dtstart_comp = component.get("dtstart")
                    dtend_comp = component.get("dtend")
                    if not dtstart_comp or not dtend_comp:
                        continue
                    
                    dtstart = dtstart_comp.dt
                    dtend = dtend_comp.dt
                    uid = str(component.get("uid"))
                    summary = str(component.get("summary") or "Reserved Block")
                    
                    events.append({
                        "uid": uid,
                        "summary": summary,
                        "start": normalize_to_date(dtstart),
                        "end": normalize_to_date(dtend)
                    })
            return events
    except Exception as e:
        logging.error(f"Failed to fetch or parse iCal feed from {url}: {e}")
    return []

@celery_app.task(name="app.tasks.sync_ical_calendars")
def sync_ical_calendars(property_id: str = None):
    """
    Celery background task to sync Airbnb and Vrbo iCal feeds for properties.
    If property_id is provided, syncs just that property. Otherwise, syncs all.
    """
    logging.info(f"Starting iCal synchronization. property_id={property_id}")
    db: Session = SessionLocal()
    try:
        # Get target properties
        if property_id:
            properties = db.query(Property).filter(Property.id == property_id).all()
        else:
            properties = db.query(Property).filter(
                (Property.airbnb_ical_import_url != None) | 
                (Property.vrbo_ical_import_url != None)
            ).all()

        for prop in properties:
            # 1. Sync Airbnb Import
            if prop.airbnb_ical_import_url:
                events = fetch_and_parse_ical(prop.airbnb_ical_import_url)
                if events:
                    # Clear future blocks
                    db.query(Reservation).filter(
                        Reservation.property_id == prop.id,
                        Reservation.ota_source == "Airbnb",
                        Reservation.check_in >= date.today()
                    ).delete()
                    
                    # Insert updated blocks
                    for ev in events:
                        if ev["end"] < date.today():
                            continue
                        res = Reservation(
                            property_id=prop.id,
                            ota_source="Airbnb",
                            external_booking_id=ev["uid"],
                            guest_name=ev["summary"],
                            check_in=ev["start"],
                            check_out=ev["end"],
                            gross_revenue=0.0,
                            tax_liability=0.0,
                            payout_status="PENDING"
                        )
                        db.add(res)
                    db.commit()
                    logging.info(f"Synced {len(events)} Airbnb bookings for property {prop.id}")

            # 2. Sync Vrbo Import
            if prop.vrbo_ical_import_url:
                events = fetch_and_parse_ical(prop.vrbo_ical_import_url)
                if events:
                    # Clear future blocks
                    db.query(Reservation).filter(
                        Reservation.property_id == prop.id,
                        Reservation.ota_source == "Vrbo",
                        Reservation.check_in >= date.today()
                    ).delete()
                    
                    # Insert updated blocks
                    for ev in events:
                        if ev["end"] < date.today():
                            continue
                        res = Reservation(
                            property_id=prop.id,
                            ota_source="Vrbo",
                            external_booking_id=ev["uid"],
                            guest_name=ev["summary"],
                            check_in=ev["start"],
                            check_out=ev["end"],
                            gross_revenue=0.0,
                            tax_liability=0.0,
                            payout_status="PENDING"
                        )
                        db.add(res)
                    db.commit()
                    logging.info(f"Synced {len(events)} Vrbo bookings for property {prop.id}")
        return True
    except Exception as e:
        logging.error(f"Error in sync_ical_calendars: {e}")
        try:
            db.rollback()
        except:
            pass
        return False
    finally:
        db.close()


