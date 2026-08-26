filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py"
with open(filepath, 'r') as f:
    content = f.read()

# 1. Remove the line that wipes the previous response string during REJECTED and FAILED_REFINEMENT
old_wipe_block = """        if filtered_data["status"] in [TaskState.FAILED_REFINEMENT.value, TaskState.REJECTED.value]:
            filtered_data["previous_response"] = \"\""""

if old_wipe_block in content:
    content = content.replace(old_wipe_block, """        # [BUG-003 Patch] Removed explicit previous_response data wipe so payload trace survives.""")
    print("Payload wipe loop successfully patched in requeue_task.")
else:
    print("Could not find the previous_response wipe block. It might have been altered.")

# 2. Fix the hardcoded string sync to actually pass Heimdall's output
old_sync_block = """        else:
            data["status"] = TaskState.REJECTED.value
            data["previous_response"] = f"Deployment failed: {output}"
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": "Deployment failed"})
            self.requeue_task(stream_id, data)"""

new_sync_block = """        else:
            data["status"] = TaskState.REJECTED.value
            data["previous_response"] = f"Deployment failed: {output}"
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": f"Deployment failed: {output}"})
            self.requeue_task(stream_id, data)"""

if old_sync_block in content:
    content = content.replace(old_sync_block, new_sync_block)
    print("API sync block successfully patched to include Heimdall's trace.")
else:
    print("Could not find the hardcoded sync block.")

with open(filepath, 'w') as f:
    f.write(content)

