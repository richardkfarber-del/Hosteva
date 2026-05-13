import os
import pytest
from app.core.mcp_client import connect_to_pgvector, ALERT_FILE_PATH
import psycopg
from psycopg import OperationalError

def test_mcp_client_critical_outage_alerting(monkeypatch):
    # Ensure the alert file doesn't exist before test
    if os.path.exists(ALERT_FILE_PATH):
        os.remove(ALERT_FILE_PATH)
    
    # We want to mock psycopg.connect to force a TimeoutError, ConnectionRefusedError, or OperationalError
    def mock_connect(*args, **kwargs):
        raise OperationalError("Simulated pgvector timeout outage")
    
    monkeypatch.setattr(psycopg, "connect", mock_connect)
    
    agent_id = "AGENT-05-ARCHITECT"
    
    with pytest.raises(OperationalError) as exc_info:
        connect_to_pgvector("postgresql://fake:fake@127.0.0.1:5432/fake", agent_id)
        
    assert "Simulated pgvector timeout outage" in str(exc_info.value)
    
    # Assert that the critical alert file was created atomically
    assert os.path.exists(ALERT_FILE_PATH)
    
    with open(ALERT_FILE_PATH, "r") as f:
        content = f.read()
        
    assert "AGENT_ID: " + agent_id in content
    assert "ERROR_TRACE: " in content
    assert "Simulated pgvector timeout outage" in content
    assert "TIMESTAMP: " in content
    
    # Cleanup
    os.remove(ALERT_FILE_PATH)
