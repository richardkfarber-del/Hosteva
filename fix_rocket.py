with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "r") as f:
    content = f.read()

# Replace the Coulson REJECTED logic in handle_auditing
old_block = """        if output and "REJECTED" in output:
            data["retry_count"] = retry_count + 1
            logger.warning(f"[{ticket_id}] Coulson REJECTED. Strike count: {data['retry_count']}")
            if data["retry_count"] >= 3:
                logger.error(f"[{ticket_id}] 3-Strike Limit Hit. Escalating to Rocket Raccoon.")
                data["status"] = TaskState.FAILED_ESCALATED.value
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {"reason": "3-Strike QA Failure"})
                prompt = f"Diagnose recurring failure for {ticket_id}. Previous task: {task_desc}. Output diagnostic report only."
                self.spawn_subagent("rocket_raccoon", prompt, ticket_id)
            else:
                data["status"] = TaskState.BACKLOG.value
                self.sync_fastapi_state(ticket_id, TaskState.BACKLOG, {"reason": output})
                self.send_telegram_alert(ticket_id, "phil_coulson", TaskState.REJECTED.value, output)"""

new_block = """        if output and "REJECTED" in output:
            data["retry_count"] = retry_count + 1
            logger.warning(f"[{ticket_id}] Coulson REJECTED. Strike count: {data['retry_count']}")
            if data["retry_count"] >= 3:
                logger.error(f"[{ticket_id}] 3-Strike Limit Hit. Escalating to Rocket Raccoon.")
                data["status"] = TaskState.FAILED_ESCALATED.value
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {"reason": "3-Strike QA Failure"})
                prompt = f"Diagnose recurring failure for {ticket_id}. Previous task: {task_desc}. Output diagnostic report only."
                self.spawn_subagent("rocket_raccoon", prompt, ticket_id)
            else:
                data["status"] = TaskState.REJECTED.value
                success = self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": output})
                self.send_telegram_alert(ticket_id, "phil_coulson", TaskState.REJECTED.value, output)
                if success:
                    data["status"] = TaskState.BUILDING.value
                    self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Re-queuing for execution"})"""

content = content.replace(old_block, new_block)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "w") as f:
    f.write(content)
