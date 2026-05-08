import requests
import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# 1. Nuke Redis Streams
r.delete("swarm:stream:tasks")
r.delete("swarm:stream:dlq")

# 2. Nuke Redis Keys
for t in ["FEAT-019", "FEAT-020", "TECH-021"]:
    r.delete(f"swarm:state:{t}")

# 3. Nuke Postgres DB entries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.swarm import SwarmState

engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/hosteva")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()
db.query(SwarmState).filter(SwarmState.ticket_id.in_(["FEAT-019", "FEAT-020", "TECH-021"])).delete()
db.commit()

# 4. Set Initial states properly via API
def push_clean(ticket_id):
    # Ensure BACKLOG
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "BACKLOG", "payload": {}})
    time.sleep(0.5)
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "REFINEMENT", "payload": {}})
    
    # Submit directly to Redis Stream with NO task description, just ticket_id
    payload = {
        "ticket_id": ticket_id, 
        "status": "REFINEMENT",
        "payload": {}
    }
    r.xadd("swarm:stream:tasks", {"payload": json.dumps(payload)})

requests.post("http://localhost:8000/state/update", json={"ticket_id": "TECH-021", "status": "DONE", "payload": {}})
push_clean("FEAT-019")
push_clean("FEAT-020")
print("Nuclear reset complete. Pipeline is pure.")
