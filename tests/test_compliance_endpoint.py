import os
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

# Force SQLite test URL globally for all tests BEFORE any app models/modules are imported
os.environ["DATABASE_URL"] = "sqlite:///./test_compliance_endpoint.db"
os.environ["INTERNAL_DATABASE_URL"] = "sqlite:///./test_compliance_endpoint.db"

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.models.compliance import MunicipalCode, PropertyCompliance
from app.models.property import Property
from app.models.host import Host
import app.db_models
from app.tasks.scraper import run_agent_compliance_scraper

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_compliance_endpoint.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def mock_geocode():
    with patch("app.api.v1.compliance.geocode_address") as mock:
        def side_effect(address):
            if address == "123 Main St":
                return {"city": "Miami", "county": "Miami-Dade County", "state": "FL", "address_components": []}
            if address == "Orlando Address":
                return {"city": "Orlando", "county": "Orange County", "state": "FL", "address_components": []}
            return {"city": "", "county": "", "state": "", "address_components": []}
        mock.side_effect = side_effect
        yield mock


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
    # Create all database tables in the test SQLite database
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # Seed host
        host = Host(
            id="host_test",
            username="test_user",
            email="test@user.com",
            password_hash="mocked_hash"
        )
        db.add(host)
        
        # Seed property
        prop = Property(
            id="property_test_1",
            user_id="host_test",
            address="123 Main St",
            city="Miami",
            state="FL",
            zip_code="33139",
            property_type="Single-Family",
            zoning_status="Pending"
        )
        db.add(prop)
        
        # Seed municipal code
        mc = MunicipalCode(
            id=uuid.UUID("11111111-2222-3333-4444-55555555555f"),
            municipality_name="Miami",
            ordinance_number="MIA-ZONING-1",
            str_prohibited=True,
            jurisdiction_type="City",
            requires_permit=True,
            permit_name="Florida DBPR License task",
            state="FL"
        )


        db.add(mc)
        
        # Seed state municipal code
        mc_state = MunicipalCode(
            id=uuid.UUID("22222222-3333-4444-5555-66666666666f"),
            municipality_name="State of Florida",
            ordinance_number="FL-STATE-LICENSE",
            str_prohibited=False,
            jurisdiction_type="State",
            requires_permit=True,
            permit_name="Florida DBPR License",
            state="FL"
        )
        db.add(mc_state)
        
        # Seed checklist item (PropertyCompliance)
        checklist_item = PropertyCompliance(
            id=uuid.UUID("abcdef12-3456-7890-abcd-ef1234567890"),
            property_id="property_test_1",
            municipal_code_id=uuid.UUID("11111111-2222-3333-4444-55555555555f"),
            is_compliant=False,
            status="PENDING",
            violation_notes="Florida DBPR License task",
            valid_period="[2026-06-04 00:00:00, 2027-06-04 00:00:00]"
        )
        db.add(checklist_item)

        # Seed Ordinances
        from app.db_models import Ordinance
        ord1 = Ordinance(
            id=1,
            jurisdiction="Miami",
            ordinance_text="Noise control and short term rentals rules in Miami city.",
            embedding=[0.1] * 1536
        )
        ord2 = Ordinance(
            id=2,
            jurisdiction="Orlando",
            ordinance_text="Registration requirement for rentals.",
            embedding=[0.2] * 1536
        )
        db.add(ord1)
        db.add(ord2)
        db.commit()

    finally:
        db.close()

    yield
    # Clean up after all tests are done
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_compliance_endpoint.db"):
        os.remove("test_compliance_endpoint.db")

client = TestClient(fastapi_app)

def test_get_compliance_missing_address():
    """
    Test that calling GET /api/v1/compliance without the address parameter
    returns a 400 Bad Request or 422 Unprocessable Entity.
    """
    response = client.get("/api/v1/compliance")
    assert response.status_code in [400, 422]

def test_get_compliance_by_address_success():
    """
    Test that calling GET /api/v1/compliance?address=123+Main+St
    returns the compliance checklist items for the property, querying
    municipal_codes and property_compliance tables.
    """
    response = client.get("/api/v1/compliance", params={"address": "123 Main St"})
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "123 Main St"
    assert data["is_compliant"] is False
    assert "checklist" in data
    assert len(data["checklist"]) == 1
    assert data["checklist"][0]["task_name"] == "Florida DBPR License task"
    assert data["checklist"][0]["status"] == "PENDING"
    assert data["checklist"][0]["is_compliant"] is False

def test_get_compliance_by_address_not_found():
    """
    Test that calling GET /api/v1/compliance?address=999+Unknown+St
    returns 404 Not Found.
    """
    response = client.get("/api/v1/compliance", params={"address": "999 Unknown St"})
    assert response.status_code == 404

def test_search_compliance_missing_query():
    """
    Test that calling GET /api/v1/compliance/search without query returns 422/400.
    """
    response = client.get("/api/v1/compliance/search")
    assert response.status_code in [400, 422]

def test_search_compliance_success():
    """
    Test successful search lookup. Under SQLite, it should fall back to standard text search.
    """
    response = client.get("/api/v1/compliance/search", params={"query": "Noise control"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["jurisdiction"] == "Miami"
    assert "Noise control" in data[0]["ordinance_text"]

def test_search_compliance_fallback_on_exception():
    """
    Test that search fallback works when we force pgvector/database query failures.
    """
    with patch("app.api.v1.compliance.generate_embedding") as mock_embed:
        mock_embed.side_effect = Exception("Service unavailable")
        response = client.get("/api/v1/compliance/search", params={"query": "Registration"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["jurisdiction"] == "Orlando"

def test_get_compliance_by_address_state_fallback():
    """
    Address with no city/county seed falls back to State of Florida rules.
    US-004: state fallback for a real city is under review — never Compliant/GREEN.
    """
    response = client.get("/api/v1/compliance", params={"address": "Orlando Address"})
    assert response.status_code == 200
    data = response.json()
    assert data["municipal_code"]["municipality_name"] == "State of Florida"
    assert data.get("is_under_review") is True
    assert data["is_compliant"] is False
    assert data.get("status") == "UNDER_REVIEW"
    assert len(data["checklist"]) == 1
    assert data["checklist"][0]["task_name"] == "Florida DBPR License"

def test_compliance_task_chat():
    """
    Test that the task chatbot endpoint returns appropriate details and links.
    """
    # 1. First seed a test task
    db = TestingSessionLocal()
    import uuid
    from app.models.compliance import PropertyCompliance
    
    task_id = uuid.uuid4()
    task = PropertyCompliance(
        id=task_id,
        property_id="property_test_1",
        municipal_code_id=uuid.UUID("11111111-2222-3333-4444-55555555555f"),
        task_name="Pasco Conditional Use Permit (CUP)",
        violation_notes="Pasco Conditional Use Permit (CUP)",
        is_compliant=False,
        status="PENDING",
        valid_period="[2026-06-04 00:00:00, 2027-06-04 00:00:00]"
    )
    db.add(task)
    db.commit()
    db.close()

    # 2. Query initial guidance
    response = client.post(f"/api/v1/compliance/tasks/{task_id}/chat", json={"query": "init_guidance"})
    assert response.status_code == 200
    data = response.json()
    assert "Conditional Use Permit" in data["response"]
    assert len(data["links"]) > 0
    assert data["prefill_data"]["property_address"] == "123 Main St"

    # 3. Query fees/costs
    response = client.post(f"/api/v1/compliance/tasks/{task_id}/chat", json={"query": "How much does it cost?"})
    assert response.status_code == 200
    data = response.json()
    assert "$250" in data["response"]

def test_agent_trigger_endpoint():
    """
    Test that triggering the scraper agent returns 202 and enqueues the Celery scraper task.
    """
    payload = {
        "property_id": "property_test_1",
        "city": "Key West",
        "county": "Monroe County",
        "state": "FL"
    }
    with patch("app.tasks.scraper.run_agent_compliance_scraper.delay") as mock_delay:
        response = client.post("/api/v1/compliance/agent/trigger", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "SCRAPING_ACTIVE"
        assert mock_delay.called

def test_fill_permit_form_endpoint():
    """
    Test that calling POST /tasks/{id}/fill-permit generates the permit ZIP package.
    """
    # 1. Create a task with a valid municipal code
    db = TestingSessionLocal()
    
    # Update state_code to have source_url so fill-permit doesn't fail early
    mc = db.query(MunicipalCode).filter(MunicipalCode.municipality_name == "Miami").first()
    mc.source_url = "https://www.miami.gov"
    mc.tax_rate_registration_fee = "12%"
    
    task_id = uuid.uuid4()
    task = PropertyCompliance(
        id=task_id,
        property_id="property_test_1",
        municipal_code_id=mc.id,
        task_name="Miami Short-Term Rental Permit",
        violation_notes="Miami Short-Term Rental Permit",
        is_compliant=False,
        status="NOT_UPLOADED",
        valid_period="[2026-06-04 00:00:00, 2027-06-04 00:00:00]"
    )
    db.add(task)
    db.commit()
    db.close()
    
    response = client.post(f"/api/v1/compliance/tasks/{task_id}/fill-permit")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert "download_url" in data
    
    # 2. Check that the ZIP file exists locally and contains the two PDFs
    import os
    import zipfile
    download_path = data["download_url"]
    assert download_path.startswith("/static/generated_permits/")
    
    local_zip_path = os.path.join("app", download_path.lstrip("/"))
    assert os.path.exists(local_zip_path)
    
    with zipfile.ZipFile(local_zip_path, 'r') as zip_file:
        files = zip_file.namelist()
        assert "permit_application.pdf" in files
        assert "submission_instructions.pdf" in files
        
    # Clean up the generated zip file
    if os.path.exists(local_zip_path):
        os.remove(local_zip_path)




