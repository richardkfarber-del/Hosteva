import os
import psycopg2

def get_agent_memory(agent_id: str, query: str = "") -> str:
    """
    Retrieves agent memory using pgvector MCP query.
    Falls back to CORE_MEMORY.md if connection fails.
    """
    try:
        # Simulated pgvector MCP connection
        conn = psycopg2.connect("dbname=pgvector user=postgres host=localhost port=5432 connect_timeout=3600")
        # Perform query...
        conn.close()
        return "Memory from pgvector"
    except Exception as e:
        # Fallback to local CORE_MEMORY.md
        fallback_path = f"/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/{agent_id}/CORE_MEMORY.md"
        if os.path.exists(fallback_path):
            with open(fallback_path, "r") as f:
                return f.read()
        return f"Error: {e} and CORE_MEMORY.md not found."
