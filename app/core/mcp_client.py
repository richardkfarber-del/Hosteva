import os
import datetime
import tempfile
import psycopg
from psycopg import OperationalError

ALERT_FILE_PATH = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/CRITICAL_ALERT.txt"

def connect_to_pgvector(dsn: str, agent_id: str):
    try:
        # Simulate connecting to pgvector using psycopg v3
        conn = psycopg.connect(dsn)
        return conn
    except (ConnectionRefusedError, TimeoutError, OperationalError) as e:
        write_critical_alert(agent_id, str(e))
        raise

def write_critical_alert(agent_id: str, error_trace: str):
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    alert_content = f"TIMESTAMP: {timestamp}\nAGENT_ID: {agent_id}\nERROR_TRACE: {error_trace}\n"
    
    # Atomic write
    dir_name = os.path.dirname(ALERT_FILE_PATH)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=dir_name)
    with os.fdopen(fd, 'w') as f:
        f.write(alert_content)
    os.replace(temp_path, ALERT_FILE_PATH)

if __name__ == "__main__":
    # Test the connection to a bogus database to trigger the alert
    try:
        connect_to_pgvector("dbname=bogus user=postgres host=127.0.0.1 port=5432 connect_timeout=3600", "AGENT-05-ARCHITECT")
    except Exception as e:
        print("Caught exception, alert file should be generated.")
