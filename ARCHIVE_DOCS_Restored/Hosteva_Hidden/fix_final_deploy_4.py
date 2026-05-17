import requests
import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# Purge any old stream cruft
r.delete("swarm:stream:tasks")
r.delete("swarm:stream:dlq")

def push_clean(ticket_id):
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "BACKLOG", "payload": {}})
    time.sleep(0.5)
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "REFINEMENT", "payload": {}})
    time.sleep(0.5)
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "BUILDING", "payload": {}})
    
    # Submit directly to Redis Stream with NO task description, just ticket_id
    payload = {
        "ticket_id": ticket_id, 
        "status": "BUILDING",
        "payload": {}
    }
    r.xadd("swarm:stream:tasks", {"payload": json.dumps(payload)})

push_clean("FEAT-019")
push_clean("FEAT-020")
print("Clean pipeline restart executed.")
