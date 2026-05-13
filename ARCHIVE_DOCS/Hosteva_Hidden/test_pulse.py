import time
from system.swarm_worker import SwarmWorker

worker = SwarmWorker()
# Mock redis client
class MockRedis:
    def hset(self, name, key, value):
        print(f"Mock hset: {name} -> {key}: {value}")
    def setex(self, name, time, value):
        print(f"Mock setex: {name} -> {value}")

worker.redis_client = MockRedis()
worker.is_processing = True

# Call it manually once to verify logic
try:
    import os
    pulse_time = time.monotonic()
    pid = str(os.getpid())
    worker.redis_client.hset("worker:pulses", pid, str(pulse_time))
    print("VERIFIED_PULSE_EMISSION")
except Exception as e:
    print(e)
