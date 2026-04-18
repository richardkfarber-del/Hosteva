import requests

def test_transition(current, target):
    # Set to current
    # We must do it by simulating valid path or directly hitting redis if possible.
    # Actually, we can just use the endpoint if we transition properly.
    pass

import redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Force state to BUILDING
r.set("swarm:state:TECH-021", '{"ticket_id":"TECH-021","status":"BUILDING","payload":{}}')
res = requests.post("http://localhost:8000/state/update", json={"ticket_id": "TECH-021", "status": "AUDITING", "payload": {}})
print("BUILDING -> AUDITING:", res.status_code, res.text)

res = requests.post("http://localhost:8000/state/update", json={"ticket_id": "TECH-021", "status": "REJECTED", "payload": {}})
print("AUDITING -> REJECTED:", res.status_code, res.text)

