import redis
import json
import requests

r = redis.Redis(host='localhost', port=6379, db=0)
r.set("swarm:state:FEAT-020", json.dumps({"status": "BACKLOG", "ticket_id": "FEAT-020"}))

# 2. Worker tries to transition to BUILDING
res = requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "FEAT-020",
    "status": "BUILDING",
    "payload": {"reason": "Refinement successful"}
})
print("BUILDING:", res.status_code, res.text)
