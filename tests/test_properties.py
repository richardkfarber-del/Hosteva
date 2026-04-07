from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_properties():
    response = client.get("/api/properties/")
    assert response.status_code == 200
