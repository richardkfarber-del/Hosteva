import redis
import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.swarm import SwarmState

r = redis.Redis(host='localhost', port=6379, db=0)

# Delete corrupted stream entirely
r.delete("swarm:stream:tasks")
r.delete("swarm:stream:dlq")

# Delete Database state
engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/hosteva")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()
db.query(SwarmState).filter(SwarmState.ticket_id.in_(["FEAT-019", "FEAT-020", "TECH-021"])).delete()
db.commit()

# Delete Redis state keys
for ticket in ["FEAT-019", "FEAT-020", "TECH-021"]:
    r.delete(f"swarm:state:{ticket}")
print("Streams and DB purged.")
