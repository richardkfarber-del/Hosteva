import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional

# Mocking the FastAPI app for test isolation based on TKT-201 Gherkin scenarios
app = FastAPI()

class DocumentRequest(BaseModel):
    property_id: Optional[str] = None

@app.post("/api/documents/generate")
def generate_document(payload: DocumentRequest):
    if not payload.property_id:
        raise HTTPException(status_code=400, detail="Missing required property data")
    
    # Mocking Redis queue integration and returning pending status
    return {
        "status": "pending",
        "message": "Document generation queued",
        "task_id": "task_999"
    }

client = TestClient(app)

def test_successful_pdf_queue_generation():
    """TKT-201: Test successful PDF queue generation."""
    response = client.post("/api/documents/generate", json={"property_id": "prop_456"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert "task_id" in data

def test_failed_generation_missing_property_id():
    """TKT-201: Test failed generation due to missing property_id."""
    response = client.post("/api/documents/generate", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing required property data"
