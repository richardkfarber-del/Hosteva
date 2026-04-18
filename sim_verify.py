import requests

# Let's send a totally bogus state to see if it bypasses validation
res = requests.post("http://localhost:8000/state/update", json={
    "ticket_id": "TEST-123",
    "status": "BOGUS_STATUS",
    "payload": {}
})
print("BOGUS_STATUS:", res.status_code, res.text)
