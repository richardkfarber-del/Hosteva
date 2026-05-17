import time
import os
import redis
import json
import threading

from system.swarm_worker import SwarmWorker

def test_pulse():
    worker = SwarmWorker(redis_url="redis://localhost:6379/0")
    worker.redis_client = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)
    worker.is_processing = True
    
    pulse_thread = threading.Thread(target=worker._background_pulse, daemon=True)
    pulse_thread.start()
    
    print("Waiting 35 seconds to allow pulse to emit...")
    time.sleep(35)
    
    pid = str(os.getpid())
    pulse_val = worker.redis_client.hget("worker:pulses", pid)
    print(f"HGET worker:pulses {pid} -> {pulse_val}")
    
    pulse_key = f"swarm:worker:pulse:{worker.worker_id}"
    key_val = worker.redis_client.get(pulse_key)
    print(f"GET {pulse_key} -> {key_val}")
    
    if pulse_val and key_val:
        print("VERIFIED")
    else:
        print("REJECTED")

if __name__ == "__main__":
    test_pulse()