import redis

r = redis.Redis(host='localhost', port=6379, db=0)
for ticket in ["FEAT-019", "FEAT-020"]:
    r.delete(f"swarm:state:{ticket}")
print("Redis keys purged")
