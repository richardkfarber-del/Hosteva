import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token

# Configure a local SQLite database for isolated unit testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the FastAPI dependency override
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create all database tables in the test SQLite database
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after all tests are done
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_temp.db"):
        os.remove("test_temp.db")

client = TestClient(app)

def test_get_properties_unauthorized():
    """
    Objective 3: Verify correct boundary handling for unauthorized states (401 Unauthorized).
    """
    response = client.get("/api/v1/properties")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_get_properties_success_pii_masked():
    """
    Objective 3: Verify proper masking of PII (Personally Identifiable Information) in payloads.
    """
    token = create_access_token(data={"sub": "testuser", "role": "host"})
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_data = {
        "properties": [
            {
                "id": "prop_9a8b7c6d",
                "address": {
                    "full_string": "123 Ocean Drive, Unit 4B, Miami Beach, FL 33139",
                    "zip_code": "33139"
                },
                "property_type": "Condo",
                "compliance_progress": {
                    "completed": 4,
                    "total": 7,
                    "percentage": 57.1
                },
                "status_badge": "pending_compliance",
                "compliance_id": "123-45-6789"
            }
        ],
        "meta": {
            "total_properties": 1,
            "platform_adoption_metrics": {
                "airbnb_linked": False,
                "vrbo_linked": False
            }
        }
    }
    
    # We patch aggregate_properties to return the mock_data instantly
    with patch("app.api.routes.properties.aggregate_properties", new_callable=AsyncMock) as mock_aggregate:
        mock_aggregate.return_value = mock_data
        response = client.get("/api/v1/properties", headers=headers)
        
        assert response.status_code == 200
        json_data = response.json()
        
        # Verify PII masking of compliance_id
        prop = json_data["properties"][0]
        assert prop["compliance_id"] == "***-**-6789"

def test_get_properties_timeout_degradation():
    """
    Objective 3: Verify graceful management of simulated service degradations or database query timeouts (503 Service Unavailable).
    """
    token = create_access_token(data={"sub": "testuser", "role": "host"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # We patch aggregate_properties to simulate a timeout or wait_for to raise TimeoutError
    with patch("app.api.routes.properties.asyncio.wait_for", side_effect=asyncio.TimeoutError):
        response = client.get("/api/v1/properties", headers=headers)
        
        assert response.status_code == 503
        assert response.json()["detail"] == "System Degraded: Database query timed out"

def test_eligibility_check_success():
    """
    Objective 2: Test compliance audit eligibility route behavior.
    """
    payload = {"address": "123 Ocean Drive, Miami, FL"}
    response = client.post("/api/compliance/eligibility-check", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "eligibility_status" in data
    assert "is_str_allowed" in data
    assert "plain_english_conditions" in data
    assert "jurisdiction" in data
