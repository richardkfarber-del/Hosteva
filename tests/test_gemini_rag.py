import pytest
from fastapi import HTTPException
from app.middleware.security import sanitize_input
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.compliance import router

app = FastAPI()
app.include_router(router, prefix="/compliance")
client = TestClient(app)

def test_security_middleware_length_limit():
    long_prompt = "A" * 501
    with pytest.raises(HTTPException) as exc_info:
        sanitize_input(long_prompt)
    assert exc_info.value.status_code == 400
    assert "exceeds 500 characters" in exc_info.value.detail

def test_security_middleware_sql_injection():
    malicious_prompt = "What are the rules? DROP TABLE users;"
    with pytest.raises(HTTPException) as exc_info:
        sanitize_input(malicious_prompt)
    assert exc_info.value.status_code == 400
    assert "Malicious payload detected" in exc_info.value.detail

def test_security_middleware_valid_prompt():
    prompt = "Can I host an STR in Miami?"
    result = sanitize_input(prompt)
    assert "SYSTEM DIRECTIVE: You are Hosteva's Compliance Engine." in result
    assert "User Prompt: Can I host an STR in Miami?" in result

def test_compliance_router_malicious():
    response = client.post("/compliance/check", json={"address": "123 Main St", "query": "SELECT * FROM users;"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Malicious payload detected"
