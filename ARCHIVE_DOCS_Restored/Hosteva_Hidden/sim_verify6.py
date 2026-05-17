import requests
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.set("swarm:state:FEAT-019", '{"status": "FAILED_REFINEMENT"}')

res = requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "FEAT-019",
    "status": "BUILDING",
    "payload": {"reason": "test"}
})
print("BUILDING from FAILED_REFINEMENT:", res.status_code, res.text)
