import requests
# Set state to AUDITING
requests.post("http://localhost:8000/state/update", json={"ticket_id": "TEST-EXACT", "status": "BACKLOG"})
requests.post("http://localhost:8000/state/update", json={"ticket_id": "TEST-EXACT", "status": "REFINEMENT"})
requests.post("http://localhost:8000/state/update", json={"ticket_id": "TEST-EXACT", "status": "BUILDING"})
requests.post("http://localhost:8000/state/update", json={"ticket_id": "TEST-EXACT", "status": "AUDITING"})
res = requests.post("http://localhost:8000/state/update", json={"ticket_id": "TEST-EXACT", "status": "REJECTED"})
print("AUDITING -> REJECTED:", res.status_code, res.text)
