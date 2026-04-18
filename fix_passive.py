with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "r") as f:
    content = f.read()

# Fix the passive handler logic to include FAILED_ESCALATED
old_block = """            elif status in [TaskState.DONE.value, TaskState.PENDING_APPROVAL.value, TaskState.BLOCKED.value, TaskState.REJECTED.value, TaskState.FAILED_REFINEMENT.value]:
                logger.info(f"[{ticket_id}] State {status} is passive. No active handler required.")
                self.ack_task(stream_id)"""

new_block = """            elif status in [TaskState.DONE.value, TaskState.PENDING_APPROVAL.value, TaskState.BLOCKED.value, TaskState.REJECTED.value, TaskState.FAILED_REFINEMENT.value, TaskState.FAILED_ESCALATED.value]:
                logger.info(f"[{ticket_id}] State {status} is passive. No active handler required.")
                self.ack_task(stream_id)"""

content = content.replace(old_block, new_block)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "w") as f:
    f.write(content)
