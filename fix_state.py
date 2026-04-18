import redis
import json
import sqlite3

r = redis.Redis(host='localhost', port=6379, db=0)
for ticket in ["FEAT-019", "FEAT-020"]:
    r.set(f"swarm:state:{ticket}", json.dumps({"status": "BACKLOG", "ticket_id": ticket}))
