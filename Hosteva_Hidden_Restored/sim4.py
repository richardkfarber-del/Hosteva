import requests

# 1. Reset state to BACKLOG
requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "FEAT-020",
    "status": "BACKLOG",
    "payload": {}
})

# 2. Worker tries to transition to BUILDING because it read REFINEMENT from the stream
res = requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "FEAT-020",
    "status": "BUILDING",
    "payload": {"reason": "Refinement successful"}
})
print("BUILDING:", res.status_code, res.text)
