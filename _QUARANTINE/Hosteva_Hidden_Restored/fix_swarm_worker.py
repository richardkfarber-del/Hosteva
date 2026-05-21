filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py"
with open(filepath, 'r') as f:
    content = f.read()

# We need to modify the requeue_task and dlq_task methods to only requeue if the API sync was successful, 
# or ensure the daemon properly handles API rejections without looping.
# Let's inspect the exact lines to patch.
