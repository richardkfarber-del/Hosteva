import pytest
import os
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Force SQLite test URL globally
os.environ["DATABASE_URL"] = "sqlite:///./test_inbox_v1.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_inbox_v1.db"

from app.main import app as fastapi_app
from app.database import Base, get_db, SessionLocal
from app.models.host import Host
from app.models.property import Property
from app.db_models import GuestMessage

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_inbox_v1.db"
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
    if os.path.exists("test_inbox_v1.db"):
        try:
            os.remove("test_inbox_v1.db")
        except:
            pass
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed host
        host = Host(
            id="host_inbox_test",
            username="inbox_host",
            email="inbox@hosteva.com",
            password_hash="mocked_hash"
        )
        db.add(host)
        
        # Seed property
        prop = Property(
            id="property_inbox_test",
            user_id="host_inbox_test",
            address="123 Ocean Dr",
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
    if os.path.exists("test_inbox_v1.db"):
        os.remove("test_inbox_v1.db")

client = TestClient(fastapi_app)

from app.core.security import get_current_user

def override_get_current_user():
    return {"username": "inbox_host", "role": "host"}

@pytest.fixture
def auth_header():
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_user
    yield {"Authorization": "Bearer fake_token"}
    fastapi_app.dependency_overrides.pop(get_current_user, None)

def test_get_inbox_unauthorized():
    response = client.get("/api/v1/inbox")
    assert response.status_code == 401

def test_receive_incoming_guest_message_and_suggested_reply():
    """
    Test receiving an incoming message.
    It should store the message and execute the suggested reply Celery task synchronously.
    """
    payload = {
        "property_id": "property_inbox_test",
        "ota_source": "Airbnb",
        "sender_name": "John Guest",
        "message_text": "Do you have high-speed wifi?"
    }
    
    response = client.post("/api/v1/inbox", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["property_id"] == "property_inbox_test"
    assert data["sender_name"] == "John Guest"
    assert data["message_text"] == "Do you have high-speed wifi?"
    
    # Verify that the suggested reply task completed synchronously
    db = TestingSessionLocal()
    msg = db.query(GuestMessage).filter(GuestMessage.property_id == "property_inbox_test").first()
    assert msg is not None
    assert msg.ai_suggested_reply is not None
    assert "wifi" in msg.ai_suggested_reply.lower() or "received" in msg.ai_suggested_reply.lower()
    db.close()

def test_get_inbox_authorized_messages(auth_header):
    """
    Test fetching the inbox for authenticated host.
    Should return all messages with their AI suggested replies.
    """
    response = client.get("/api/v1/inbox", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["sender_name"] == "John Guest"
    assert data[0]["ai_suggested_reply"] is not None
    assert data[0]["is_replied"] == 0

def test_reply_to_message_success(auth_header):
    """
    Test submitting a reply to a message.
    Should mark the message as replied in the DB.
    """
    db = TestingSessionLocal()
    msg = db.query(GuestMessage).filter(GuestMessage.property_id == "property_inbox_test").first()
    message_id = msg.id
    db.close()
    
    response = client.post(
        f"/api/v1/inbox/{message_id}/reply",
        json={"reply_text": "Yes, we have 100Mbps fiber wifi."},
        headers=auth_header
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify DB update
    db = TestingSessionLocal()
    updated_msg = db.query(GuestMessage).filter(GuestMessage.id == message_id).first()
    assert updated_msg.is_replied == 1
    db.close()
