import requests
import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# Purge any old stream cruft
r.delete("swarm:stream:tasks")
r.delete("swarm:stream:dlq")

def push(ticket_id):
    # Ensure BACKLOG
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "BACKLOG", "payload": {}})
    time.sleep(0.5)
    
    # Update state to REFINEMENT
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "REFINEMENT", "payload": {}})
    
    # Submit directly to Redis Stream
    payload = {
        "ticket_id": ticket_id, 
        "status": "REFINEMENT",
        "payload": {}
    }
    r.xadd("swarm:stream:tasks", {"payload": json.dumps(payload)})

push("FEAT-019")
push("FEAT-020")
print("Direct Redis injection complete. DAG cleared.")
