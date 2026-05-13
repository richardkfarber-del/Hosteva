import redis
import json

r = redis.Redis.from_url("redis://localhost:6379/9")
r.flushdb()

# Task 1: Happy Path
r.rpush("swarm:queue:tasks", json.dumps({
    "ticket_id": "TEST-HAPPY-01", 
    "status": "PENDING", 
    "task": "Test happy path where Coulson verifies.", 
    "retry_count": 0
}))

# Task 2: 3-Strike Escalation
r.rpush("swarm:queue:tasks", json.dumps({
    "ticket_id": "TEST-STRIKE-02", 
    "status": "PENDING", 
    "task": "Test 3 strikes where Coulson constantly rejects.", 
    "retry_count": 0
}))

# Task 3: Malformed JSON
r.rpush("swarm:queue:tasks", "{malformed_json_here: true]")

print("Injected tasks into Redis DB 9.")