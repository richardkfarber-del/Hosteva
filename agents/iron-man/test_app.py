from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.dashboard_api import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

response = client.get("/api/v1/dashboard/overview")
print("Status Code:", response.status_code)
print("JSON payload:", response.json())
