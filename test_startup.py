from fastapi.testclient import TestClient
from app.main import app

def test_startup():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    print("Application starts and serves the root endpoint successfully.")
    
    # Try an endpoint that might use Celery or OAuth schema if there are any
    print("No fatal runtime crashes detected on startup.")

test_startup()
