import pytest
import os
import uuid
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Force SQLite test URL globally
os.environ["DATABASE_URL"] = "sqlite:///./test_calendar_v1.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_calendar_v1.db"

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.property import Property
from app.db_models import Reservation
from app.tasks.calendar import sync_ical_calendars

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_calendar_v1.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def bind_session_local():
    from app.database import SessionLocal
    SessionLocal.configure(bind=engine)
    yield



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_db():
    original_override = fastapi_app.dependency_overrides.get(get_db)
    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield
    if original_override is not None:
        fastapi_app.dependency_overrides[get_db] = original_override
    else:
        fastapi_app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    if os.path.exists("test_calendar_v1.db"):
        try:
            os.remove("test_calendar_v1.db")
        except:
            pass
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        # Seed property
        prop = Property(
            id="property_cal_test",
            user_id="host_cal_test",
            address="101 Ocean Dr",
            city="Miami Beach",
            state="FL",
            zip_code="33139"
        )
        db.add(prop)
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_calendar_v1.db"):
        os.remove("test_calendar_v1.db")

client = TestClient(fastapi_app)

def test_sync_ical_registration_success():
    """
    Test registering iCal import urls.
    Should generate a secure token and return the export endpoint link.
    """
    payload = {
        "property_id": "property_cal_test",
        "airbnb_ical_import_url": "http://mock-ota.com/airbnb.ics",
        "vrbo_ical_import_url": "http://mock-ota.com/vrbo.ics"
    }
    
    with patch("app.api.v1.operations.sync_ical_calendars.delay") as mock_celery:
        response = client.post("/api/v1/operations/sync-ical", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["airbnb_ical_import_url"] == "http://mock-ota.com/airbnb.ics"
        assert data["vrbo_ical_import_url"] == "http://mock-ota.com/vrbo.ics"
        assert "hosteva_ical_export_token" in data
        assert "hosteva_ical_export_url" in data
        
        # Verify database fields updated
        db = TestingSessionLocal()
        prop = db.query(Property).filter(Property.id == "property_cal_test").first()
        assert prop.airbnb_ical_import_url == "http://mock-ota.com/airbnb.ics"
        assert prop.vrbo_ical_import_url == "http://mock-ota.com/vrbo.ics"
        assert prop.hosteva_ical_export_token is not None
        db.close()
        
        # Verify background Celery task triggered
        mock_celery.assert_called_once_with("property_cal_test")

def test_sync_ical_task_execution():
    """
    Test running background sync_ical_calendars Celery task.
    Should download feed, parse events, and save as Reservations in DB.
    """
    mock_airbnb_content = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "BEGIN:VEVENT\n"
        "UID:booking_airbnb_999\n"
        "SUMMARY:Jane Doe\n"
        "DTSTART;VALUE=DATE:20281201\n"
        "DTEND;VALUE=DATE:20281205\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    ).encode("utf-8")

    mock_vrbo_content = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "BEGIN:VEVENT\n"
        "UID:booking_vrbo_999\n"
        "SUMMARY:Jane Doe\n"
        "DTSTART;VALUE=DATE:20281201\n"
        "DTEND;VALUE=DATE:20281205\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    ).encode("utf-8")

    def mock_get_side_effect(url, *args, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        if "airbnb" in url:
            mock_response.content = mock_airbnb_content
        else:
            mock_response.content = mock_vrbo_content
        return mock_response
    
    with patch("app.tasks.calendar.requests.get", side_effect=mock_get_side_effect) as mock_get:


        
        # Diagnostic print
        db_diag = TestingSessionLocal()
        props_diag = db_diag.query(Property).all()
        for p in props_diag:
            print("PROPERTY IN DB:", p.id, "airbnb:", p.airbnb_ical_import_url, "vrbo:", p.vrbo_ical_import_url)
        db_diag.close()


        # Run sync task directly
        res = sync_ical_calendars("property_cal_test")
        assert res is True


        
        # Verify Reservation in database
        # Verify Reservation in database
        db = TestingSessionLocal()
        bookings = db.query(Reservation).filter(Reservation.property_id == "property_cal_test").all()
        assert len(bookings) == 2
        
        # Sort by external_booking_id to assert cleanly
        bookings_sorted = sorted(bookings, key=lambda r: r.external_booking_id)
        
        assert bookings_sorted[0].external_booking_id == "booking_airbnb_999"
        assert bookings_sorted[0].guest_name == "Jane Doe"
        assert bookings_sorted[0].check_in == date(2028, 12, 1)
        assert bookings_sorted[0].check_out == date(2028, 12, 5)
        assert bookings_sorted[0].ota_source == "Airbnb"
        
        assert bookings_sorted[1].external_booking_id == "booking_vrbo_999"
        assert bookings_sorted[1].guest_name == "Jane Doe"
        assert bookings_sorted[1].check_in == date(2028, 12, 1)
        assert bookings_sorted[1].check_out == date(2028, 12, 5)
        assert bookings_sorted[1].ota_source == "Vrbo"
        
        db.close()


def test_export_calendar_success():
    """
    Test GET /api/v1/operations/calendar/export with valid token.
    Should return standard iCalendar attachment payload.
    """
    db = TestingSessionLocal()
    prop = db.query(Property).filter(Property.id == "property_cal_test").first()
    token = prop.hosteva_ical_export_token
    db.close()
    
    response = client.get("/api/v1/operations/calendar/export", params={"token": token})
    assert response.status_code == 200
    assert response.headers.get("content-type") == "text/calendar; charset=utf-8"
    assert "booking_airbnb_999" in response.text
    assert "Jane Doe" in response.text

def test_export_calendar_invalid_token():
    response = client.get("/api/v1/operations/calendar/export", params={"token": "invalid_tok"})
    assert response.status_code == 404
