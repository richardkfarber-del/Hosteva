import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_workflow():
    # Use a unique username and email to prevent conflict with existing DB records
    unique_suffix = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_suffix}"
    email = f"test_{unique_suffix}@hosteva.com"
    password = "SuperSecretPassword123!"

    # 1. Registration Test
    reg_response = client.post(
        "/api/user/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    assert reg_response.status_code == 200
    reg_data = reg_response.json()
    assert reg_data["username"] == username
    assert reg_data["status"] == "success"

    # 2. Duplicate Registration Test (should fail)
    dup_response = client.post(
        "/api/user/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    assert dup_response.status_code == 400
    assert "detail" in dup_response.json()

    # 3. Login Test (Valid)
    login_response = client.post(
        "/api/user/login",
        data={
            "username": username,
            "password": password
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    token = login_data["access_token"]

    # 4. Login Test (Invalid password)
    bad_login_response = client.post(
        "/api/user/login",
        data={
            "username": username,
            "password": "WrongPassword123"
        }
    )
    assert bad_login_response.status_code == 401
    assert bad_login_response.json()["detail"] == "Incorrect username or password"

    # 5. Profile Check (With Auth)
    profile_response = client.get(
        "/api/user/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["username"] == username
    assert profile_data["email"] == email

    # 6. Profile Check (Without Auth)
    no_auth_response = client.get("/api/user/me")
    assert no_auth_response.status_code == 401
