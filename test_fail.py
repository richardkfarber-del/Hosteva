import redis
import requests
import json
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
# Inspect Redis directly for the current state of TECH-021
print("Current Redis state:", r.get("swarm:state:TECH-021"))
