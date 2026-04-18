import requests
import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)

def push(ticket_id):
    # Ensure BACKLOG
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "BACKLOG", "payload": {}})
    time.sleep(0.5)
    
    # Update state to REFINEMENT
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "REFINEMENT", "payload": {}})
    
    # Submit directly to Redis Stream (bypassing FastAPI Pydantic schema which strips 'task')
    # For REFINEMENT, we still need to pass the task string ONE LAST TIME so Vision knows what to refine.
    # Once TECH-021 is deployed, this script won't be needed anymore.
    payload = {
        "ticket_id": ticket_id, 
        "status": "REFINEMENT", 
        "task": "Secretary's Orders: We have uncovered a major architectural anti-pattern. Redis is currently being used to pass ephemeral ticket details (task_desc), which gets dropped during fallback loops causing blank prompts. The Secretary mandates that Redis must ONLY track state: ticket_id, status, and response from the previous agent. Draft a formal Gherkin ticket on project_board.md detailing this rewrite for the swarm_worker.py daemon. The acceptance criteria MUST explicitly state that the daemon will no longer pass task_desc strings to agents. Instead, the daemon's prompts must instruct agents to use their tools to read project_board.md to find their ticket requirements before executing their task.",
        "payload": {}
    }
    import json
    r.xadd("swarm:stream:tasks", {"payload": json.dumps(payload)})

push("TECH-021")
print("Direct Redis injection complete.")
