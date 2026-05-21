import time
import threading
import json
import redis
from system.swarm_worker import SwarmWorker

def test_worker():
    worker = SwarmWorker()
    worker.redis_client = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)
    worker.is_processing = True
    
    pulse_thread = threading.Thread(target=worker._background_pulse, daemon=True)
    pulse_thread.start()
    
    print("Worker processing simulated. Wait for 35 seconds to see pulse...")
    time.sleep(35)
    
    keys = worker.redis_client.keys("swarm:worker:pulse:*")
    print("Found pulse keys:", keys)
    for k in keys:
        print(k, "=>", worker.redis_client.get(k))

if __name__ == "__main__":
    test_worker()
