import requests
import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def push(ticket_id):
    # Ensure BACKLOG
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "BACKLOG", "payload": {}})
    time.sleep(0.5)
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "REFINEMENT", "payload": {}})
    time.sleep(0.5)
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "BUILDING", "payload": {}})
    
    # Submit directly to Redis Stream (Strike 2)
    payload = {
        "ticket_id": ticket_id, 
        "status": "BUILDING",
        "retry_count": 2,
        "payload": {}
    }
    r.xadd("swarm:stream:tasks", {"payload": json.dumps(payload)})

push("FEAT-019")
push("FEAT-020")
print("Direct Redis injection for Strike 2 complete.")
