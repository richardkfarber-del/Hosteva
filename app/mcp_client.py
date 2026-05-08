import os
import time
import datetime
from contextlib import contextmanager

class MCPClient:
    def __init__(self, agent_id="AGENT-UNKNOWN"):
        self.agent_id = agent_id

    def connect_to_pgvector(self):
        try:
            # Simulate an attempt to connect to pgvector
            import psycopg2
            # Will raise OperationalError if connection fails, but here we'll just mock the behavior
            conn = psycopg2.connect("dbname=postgres user=postgres host=localhost port=5432")
            return conn
        except (ConnectionRefusedError, TimeoutError) as e:
            self._handle_critical_outage(e)
            raise
        except Exception as e:
            if type(e).__name__ == 'OperationalError':
                self._handle_critical_outage(e)
            raise

    def get_memory(self, query=""):
        """
        Retrieves agent memory. Wraps pgvector MCP query in try/except.
        Falls back to CORE_MEMORY.md if connection fails.
        """
        try:
            conn = self.connect_to_pgvector()
            # Simulate pgvector fetch
            # cur = conn.cursor()
            # cur.execute(...)
            return "Memory from pgvector"
        except Exception as e:
            # Fallback to local CORE_MEMORY.md
            return self._read_core_memory_fallback()

    def _read_core_memory_fallback(self):
        # We need to map agent_id to folder, but we can search for the core memory or use a direct path
        # Assuming the standard path structure
        # Just to keep it simple, we read it locally
        import glob
        # The agent ID is like AGENT-05-ARCHITECT, we might need to find the folder. 
        # But we can just use a wildcard for demonstration or know the specific agent path
        agent_dir_name = None
        
        # Mapping or finding
        base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents"
        for d in os.listdir(base_dir):
            if os.path.isdir(os.path.join(base_dir, d)):
                identity_path = os.path.join(base_dir, d, "IDENTITY.md")
                if os.path.exists(identity_path):
                    with open(identity_path, "r") as f:
                        if self.agent_id in f.read():
                            agent_dir_name = d
                            break
        
        if not agent_dir_name:
            # fallback if not found
            return "Minimal CORE MEMORY (Fallback)"

        core_path = os.path.join(base_dir, agent_dir_name, "CORE_MEMORY.md")
        if os.path.exists(core_path):
            with open(core_path, "r") as f:
                return f.read()
        return "Minimal CORE MEMORY (Fallback)"

    def _handle_critical_outage(self, error: Exception):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        alert_msg = f"[{timestamp}] CRITICAL PGVECTOR OUTAGE\n"
        alert_msg += f"Agent ID: {self.agent_id}\n"
        alert_msg += f"Error Trace: {type(error).__name__}: {str(error)}\n"
        alert_msg += "-" * 40 + "\n"
        
        alert_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/CRITICAL_ALERT.txt"
        
        # Atomic write
        temp_path = alert_path + ".tmp"
        with open(temp_path, "w") as f:
            f.write(alert_msg)
        os.replace(temp_path, alert_path)

# For testing / verification purposes
if __name__ == "__main__":
    client = MCPClient(agent_id="AGENT-05-ARCHITECT")
    try:
        # We can force an error to test the interceptor
        class OperationalError(Exception):
            pass
        raise OperationalError("server closed the connection unexpectedly")
    except Exception as e:
        client._handle_critical_outage(e)
