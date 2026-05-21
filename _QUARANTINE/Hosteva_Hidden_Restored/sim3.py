import requests

# 1. Set to REFINEMENT
requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "FEAT-020",
    "status": "REFINEMENT",
    "payload": {}
})

# 2. Try BUILDING
res = requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "FEAT-020",
    "status": "BUILDING",
    "payload": {"reason": "Refinement successful"}
})
print("BUILDING:", res.status_code, res.text)
