import requests
import json
import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)

desc_019 = """The Executive Board has established a strict Test-Driven Development (TDD) Mandate. The MVP Dashboard API and UI components must have complete automated test coverage integrated into the pipeline before proceeding with further feature builds. This ticket establishes the baseline testing infrastructure and coverage metrics for the GET /api/v1/properties route and the dashboard.html UI component.
Given the Test-Driven Development (TDD) Mandate is active, When Iron Man writes tests for the MVP Dashboard API (GET /api/v1/properties), Then he MUST cover 1) positive PII masking response, 2) HTTP 401 unauthorized errors, and 3) simulated HTTP 503 timeout gracefully handled.
Given automated coverage is complete, When Captain America executes pytest tests/, Then the suite MUST pass 100% green before any future code is pushed."""

desc_020 = """Implement the core PostgreSQL data models and alembic database migrations for the municipal compliance engine. This requires translating the architecture defined in SPIKE-007 into physical SQLAlchemy models, enforcing strict append-only temporal versioning to prevent data overwrites, and applying rigorous GiST and B-Tree indexing strategies for performant spatial/temporal queries.
Given the tables require append-only temporal versioning, When writing the schema, Then Iron Man MUST physically implement the trg_close_expired_compliance PostgreSQL Trigger to strictly prevent historical overwrite operations.
Given concurrent queries will hammer the property_compliance table, When designing the schema, Then Iron Man MUST build composite GiST or B-Tree indexes across property_id and the valid_period tsrange column to mathematically guarantee O(log N) lookup times (Thanos constraint)."""

def push(ticket_id, task_desc):
    # Back to BACKLOG
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "BACKLOG", "payload": {}})
    time.sleep(1)
    
    # Update state to REFINEMENT
    requests.post("http://localhost:8000/state/update", json={"ticket_id": ticket_id, "status": "REFINEMENT", "payload": {}})
    
    # Submit to Stream WITH task payload
    payload = {"ticket_id": ticket_id, "status": "REFINEMENT", "task": task_desc}
    requests.post("http://localhost:8000/state/submit", json=payload)

push("FEAT-019", desc_019)
push("FEAT-020", desc_020)
print("Done")
