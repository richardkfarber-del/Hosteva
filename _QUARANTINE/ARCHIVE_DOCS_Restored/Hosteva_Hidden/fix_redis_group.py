import redis
r = redis.Redis(host='localhost', port=6379, db=0)
try:
    r.xgroup_destroy("swarm:stream:tasks", "swarm_group")
except:
    pass
try:
    r.xgroup_create("swarm:stream:tasks", "swarm_group", id="0", mkstream=True)
except Exception as e:
    print(f"Failed to create group: {e}")
print("Group recreated.")
