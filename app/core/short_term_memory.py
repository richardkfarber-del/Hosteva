import json
import os
import fcntl
import time
from typing import Optional, Dict, Any

def append_to_short_term_memory(
    agent_id: str, 
    text: str, 
    metadata: Optional[Dict[str, Any]] = None, 
    filepath: str = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/short_term_memory.jsonl"
) -> None:
    """
    Appends a new memory entry to the short-term JSONL log file.
    Implements fcntl file locking to prevent race conditions from concurrent agent writes.
    """
    entry = {
        "agent_id": agent_id,
        "text": text,
        "metadata": metadata or {},
        "timestamp": time.time()
    }
    
    with open(filepath, "a") as f:
        # Acquire an exclusive lock before writing
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
        finally:
            # Release the lock
            fcntl.flock(f, fcntl.LOCK_UN)
