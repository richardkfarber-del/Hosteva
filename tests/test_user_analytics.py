import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.host import Host
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.core.security import get_current_user

client = TestClient(app)

# Use in-memory SQLite for testing DB interactions
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analytics.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "testuser", "role": "host"}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed a test host
    test_host = Host(username="testuser", email="test@example.com", password_hash="hash", subscription_tier="pro")
    db.add(test_host)
    db.commit()
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_get_user_analytics():
    response = client.get("/api/user/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "subscription_tier" in data
    assert data["subscription_tier"] == "pro"
    
    assert "recent_queries" in data
    assert isinstance(data["recent_queries"], list)
    assert len(data["recent_queries"]) == 3
    assert data["recent_queries"][0]["query"] == "What are the STR laws in Miami?"
