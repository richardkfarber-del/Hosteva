import pytest
from app.main import app
from fastapi.testclient import TestClient
from app.core.security import get_current_user
from app.database import get_db

client = TestClient(app)

class MockHost:
    subscription_tier = "Pro"

class MockQuery:
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return MockHost()

class MockDB:
    def query(self, *args, **kwargs):
        return MockQuery()

def override_get_current_user():
    return {"username": "testuser", "role": "host"}

def override_get_db():
    yield MockDB()

def test_get_user_analytics():
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    
    response = client.get("/api/user/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "subscription_tier" in data
    assert data["subscription_tier"] == "Pro"
    
    assert "recent_queries" in data
    assert isinstance(data["recent_queries"], list)
    assert len(data["recent_queries"]) == 3
    assert data["recent_queries"][0]["query"] == "What are the STR laws in Miami?"
    
    app.dependency_overrides.clear()
