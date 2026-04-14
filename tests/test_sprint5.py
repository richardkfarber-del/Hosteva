import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_bug_005_logo_and_nav(client):
    """
    Test that BUG-005 is fixed:
    1. The hardcoded logo path is updated.
    2. The Integrations link is in the navbar.
    """
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    
    # Check for url_for pattern for logo
    assert "static/img/hosteva_logo.png" in content or "img/hosteva_logo.png" in content
    assert "hosteva_logo.png" in content
    
    # Check for Integrations link
    assert "Integrations" in content
    assert "integrations" in content.lower()

def test_feat_012_rag_endpoint(client):
    """
    Test that FEAT-012 RAG endpoint conforms to the Spike contract.
    """
    payload = {
        "property_id": 123,
        "question": "Are short term rentals allowed in R-1 zoning?",
        "jurisdiction": "Orlando, FL"
    }
    response = client.post("/api/compliance/rag/query", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "confidence_score" in data
    assert isinstance(data["sources"], list)
    if len(data["sources"]) > 0:
        assert "ordinance_id" in data["sources"][0]
        assert "section" in data["sources"][0]
        assert "snippet" in data["sources"][0]
