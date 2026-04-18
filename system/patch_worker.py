with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "r") as f:
    content = f.read()

# Fix 1: Add the webhook to FAILED_REFINEMENT
old_block = """            if output and "FAILED_REFINEMENT" in output:
                data["status"] = TaskState.FAILED_REFINEMENT.value
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_REFINEMENT, {"reason": output})"""
new_block = """            if output and "FAILED_REFINEMENT" in output:
                data["status"] = TaskState.FAILED_REFINEMENT.value
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_REFINEMENT, {"reason": output})
                self.send_telegram_alert(ticket_id, "vision", TaskState.FAILED_REFINEMENT.value, output)"""
content = content.replace(old_block, new_block)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "w") as f:
    f.write(content)
