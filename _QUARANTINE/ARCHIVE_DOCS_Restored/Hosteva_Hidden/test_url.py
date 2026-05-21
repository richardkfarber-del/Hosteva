from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.get("/")
print("STATUS:", response.status_code)
if response.status_code != 200:
    print(response.text)
