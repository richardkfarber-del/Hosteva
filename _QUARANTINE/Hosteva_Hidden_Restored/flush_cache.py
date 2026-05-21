import redis
r = redis.from_url("redis://localhost:6379/0")
r.delete("swarm:state:FEAT-019")
r.delete("swarm:routing_strikes:FEAT-019")
print("Redis cache for FEAT-019 flushed.")
