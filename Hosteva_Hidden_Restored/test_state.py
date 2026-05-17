import requests
import json
import redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
print("REDIS TECH-021:", r.get("swarm:state:TECH-021"))
