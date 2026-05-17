import requests
req = {
    "ticket_id": "FEAT-019",
    "status": "BUILDING",
    "payload": {"reason": "test"}
}
res = requests.post("http://localhost:8000/state/update", json=req)
print(res.status_code, res.text)
