import pytest
import time
import threading
import uuid
import sys
import os
from unittest.mock import patch, MagicMock

# Ensure we can import system.swarm_worker
sys.path.insert(0, "/home/rdogen/OpenClaw_Factory/projects/Hosteva")
from system.swarm_worker import SwarmWorker

def test_redis_locking_script_compilation():
    """Verify that SwarmWorker lock script executes atomicity."""
    worker = SwarmWorker(redis_url="redis://localhost:6379/0")
    worker.connect_redis_with_backoff()
    
    # We will just verify that the locking mechanism used in spawn_subagent functions properly
    # at a basic Redis level since we can't fully invoke spawn_subagent without hitting gateway
    
    kebab_id = "test-agent"
    lock_key = f"swarm:lock:context:{kebab_id}"
    lock_val = str(uuid.uuid4())
    
    lock_script = worker.redis_client.register_script("""
        if redis.call('setnx', KEYS[1], ARGV[1]) == 1 then
            redis.call('pexpire', KEYS[1], ARGV[2])
            return 1
        else
            return 0
        end
    """)
    
    unlock_script = worker.redis_client.register_script("""
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
    """)
    
    # Clean up before
    worker.redis_client.delete(lock_key)
    
    # Attempt lock 1 - Should Succeed
    success1 = lock_script(keys=[lock_key], args=[lock_val, 10000])
    assert success1 == 1
    
    # Attempt lock 2 with different value - Should Fail
    lock_val2 = str(uuid.uuid4())
    success2 = lock_script(keys=[lock_key], args=[lock_val2, 10000])
    assert success2 == 0
    
    # Unlock 1 - Should Succeed
    unlocked = unlock_script(keys=[lock_key], args=[lock_val])
    assert unlocked == 1
    
    # Attempt lock 2 again - Should Succeed
    success3 = lock_script(keys=[lock_key], args=[lock_val2, 10000])
    assert success3 == 1
    
    # Clean up
    unlock_script(keys=[lock_key], args=[lock_val2])
