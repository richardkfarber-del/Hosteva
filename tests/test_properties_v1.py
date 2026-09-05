import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the app is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token
from app.models.host import Host
from app.models.property import Property

# Configure local SQLite database for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_properties_v1.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def _properties_db_override():
    # Re-apply each test: other modules overwrite dependency_overrides at import.
    original = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    from app.database import SessionLocal
    SessionLocal.configure(bind=engine)
    yield
    if original is not None:
        app.dependency_overrides[get_db] = original
    else:
        app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Force tables creation
    import app.db_models
    Base.metadata.create_all(bind=engine)
    
    # Seed a host for testing
    db = TestingSessionLocal()
    try:
        host = Host(
            id="host_test_v1",
            username="testuser",
            email="test@user.com",
            password_hash="mocked_hash"
        )
        db.add(host)
        db.commit()
    finally:
        db.close()
        
    yield
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_properties_v1.db"):
        os.remove("test_properties_v1.db")

client = TestClient(app)

def test_post_properties_unauthorized():
    """
    Test that calling POST /api/v1/properties without token returns 401.
    """
    payload = {
        "address": {
            "address": "123 Ocean Drive",
            "city": "Miami",
            "state": "FL",
            "zip_code": "33139"
        },
        "property_type": "Condo"
    }
    response = client.post("/api/v1/properties", json=payload)
    assert response.status_code == 401

@patch("app.routers.properties.fetch_real_property_image")
def test_post_properties_success(mock_fetch_image):
    """
    Test that calling POST /api/v1/properties with valid token and payload
    inserts the property and returns 201.
    """
    mock_fetch_image.return_value = "/static/img/fallback_house.jpg"
    
    token = create_access_token(data={"sub": "testuser", "role": "host"})
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "address": {
            "address": "456 Ocean Drive",
            "city": "Miami Beach",
            "state": "FL",
            "zip_code": "33139"
        },
        "property_type": "Condo",
        "compliance_data": {
            "zoning_status": "Compliant",
            "hoa_status": False,
            "required_permits": ["Florida DBPR License task"],
            "local_restrictions": {"stay_limit": "30 days min"}
        }
    }
    
    response = client.post("/api/v1/properties", json=payload, headers=headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["address"] == "456 Ocean Drive"
    assert data["city"] == "Miami Beach"
    assert data["state"] == "FL"
    assert data["zip_code"] == "33139"
    assert data["property_type"] == "Condo"
    assert data["hoa_status"] is False
    assert data["zoning_status"] == "Compliant"
    assert "id" in data

    # Verify database state
    db = TestingSessionLocal()
    try:
        db_prop = db.query(Property).filter(Property.address == "456 Ocean Drive").first()
        assert db_prop is not None
        assert db_prop.user_id == "host_test_v1"
        assert db_prop.zoning_status == "Compliant"
    finally:
        db.close()

def test_post_properties_validation_error():
    """
    Test that calling POST /api/v1/properties with invalid payload returns 422.
    """
    token = create_access_token(data={"sub": "testuser", "role": "host"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Missing required city in address
    payload = {
        "address": {
            "address": "456 Ocean Drive",
            "state": "FL"
        },
        "property_type": "Condo"
    }
    response = client.post("/api/v1/properties", json=payload, headers=headers)
    assert response.status_code == 422
