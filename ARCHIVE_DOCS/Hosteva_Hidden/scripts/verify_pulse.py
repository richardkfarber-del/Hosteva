import redis
import json
r = redis.Redis(host='localhost', port=6379, db=0)
print("Keys:", r.keys("swarm:worker:pulse:*"))
