import redis
import json
import requests

r = redis.Redis(host='localhost', port=6379, db=0)
r.set("swarm:state:FEAT-021", json.dumps({"status": "REFINEMENT", "ticket_id": "FEAT-021"}))

res = requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "FEAT-021",
    "status": "BUILDING",
    "payload": {}
})
print("BUILDING from REFINEMENT:", res.status_code, res.text)
