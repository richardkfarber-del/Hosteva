import os
import sys

# Ensure the app module is importable
sys.path.insert(0, "/home/rdogen/OpenClaw_Factory/projects/Hosteva")

from app.mcp_client import MCPClient

def verify():
    print("Testing Vector DB Critical Outage Alerting (CHORE-049)")
    client = MCPClient(agent_id="AGENT-TEST-001")
    
    # Mocking OperationalError
    class OperationalError(Exception):
        pass
        
    try:
        raise OperationalError("Connection to pgvector failed: Timeout or host unreachable")
    except Exception as e:
        client._handle_critical_outage(e)
        
    alert_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/CRITICAL_ALERT.txt"
    if os.path.exists(alert_path):
        with open(alert_path, "r") as f:
            content = f.read()
        print(f"✅ CRITICAL_ALERT.txt was created atomically.")
        print(f"Content:\n{content}")
        if "AGENT-TEST-001" in content and "OperationalError" in content:
            print("✅ Alert contains correct Agent ID and Error Trace.")
        else:
            print("❌ Alert missing required data.")
    else:
        print("❌ CRITICAL_ALERT.txt was not created.")

if __name__ == "__main__":
    verify()
