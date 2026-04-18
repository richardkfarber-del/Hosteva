import requests

# Test: Send request without state in redis (simulating BACKLOG)
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.delete("swarm:state:FEAT-022")

res = requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "FEAT-022",
    "status": "BUILDING",
    "payload": {}
})
print("BUILDING from BACKLOG:", res.status_code, res.text)
