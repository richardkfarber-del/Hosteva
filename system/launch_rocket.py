import json
import redis
from pydantic import BaseModel

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
dlq_items = r.lrange("swarm:queue:dlq", 0, -1)

for item in dlq_items:
    try:
        data = json.loads(item)
        if data.get("ticket_id") == "TICKET-04":
            print(json.dumps(data, indent=2))
            break
    except:
        pass
