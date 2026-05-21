import redis
import os
import requests

r = redis.Redis(host='localhost', port=6379, db=0)

# Delete corrupted stream entirely
r.delete("swarm:stream:tasks")
r.delete("swarm:stream:dlq")

print("Streams purged.")
