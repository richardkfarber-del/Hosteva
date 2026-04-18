import sys

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "r") as f:
    content = f.read()

old_logic = """        if audit_status == "VERIFIED":
            logger.info(f"[{ticket_id}] Coulson VERIFIED. Transitioning ticket to TESTING.")
            self.redis_client.delete(f"swarm:strikes:{ticket_id}")
            data["status"] = TaskState.TESTING.value
            data["previous_response"] = coulson_output
            self.requeue_task(stream_id, data)
            self.sync_fastapi_state(ticket_id, TaskState.TESTING, {"coulson_audit": coulson_output})
            self.send_telegram_alert(ticket_id, "phil_coulson", TaskState.TESTING.value, coulson_output)
        else:
            retry_count = self.redis_client.incr(f"swarm:strikes:{ticket_id}")
            logger.warning(f"[{ticket_id}] Coulson REJECTED. Strike count: {retry_count}")
            
            if retry_count >= 3:
                logger.error(f"[{ticket_id}] 3-Strike Limit Hit. Escalating to Rocket Raccoon.")
                
                rocket_prompt = (
                    f"A ticket has failed 3 consecutive times.\\n\\n"
                    f"Ticket: {ticket_id}\\n"
                    f"Use your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\\n"
                    f"Execution Output: {exec_output}\\n"
                    f"Coulson Audit Failure: {coulson_output}\\n\\n"
                    f"DIRECTIVE: Perform a root-cause diagnostic on this failure loop. Propose a permanent fix. Do not write the code. Output your recommendation for the Secretary's review."
                )
                
                rocket_analysis = self.spawn_subagent("rocket_raccoon", rocket_prompt, ticket_id)
                
                data["status"] = TaskState.FAILED_ESCALATED.value
                self.redis_client.delete(f"swarm:strikes:{ticket_id}")
                self.dlq_task(stream_id, data)
                
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {
                    "reason": "3 strikes hit", 
                    "last_audit": coulson_output,
                    "rocket_diagnostic": rocket_analysis
                })
                self.send_telegram_alert(ticket_id, "rocket_raccoon", TaskState.FAILED_ESCALATED.value, rocket_analysis)
            else:
                # Transition to REJECTED first to satisfy FastAPI state machine
                sync_success = self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": "Rejected by Coulson", "retry_count": retry_count})
                
                # If sync is successful, then move it back to BUILDING
                if sync_success:
                    self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Re-queueing after rejection"})
                    data["status"] = TaskState.BUILDING.value
                    data["previous_response"] = f"PREVIOUS REJECTION REASON:\\n{coulson_output}"
                    self.requeue_task(stream_id, data)
                
                self.send_telegram_alert(ticket_id, "phil_coulson", "REJECTED", coulson_output)"""

new_logic = """        if audit_status == "VERIFIED":
            logger.info(f"[{ticket_id}] Coulson VERIFIED. Transitioning ticket to TESTING.")
            data["status"] = TaskState.TESTING.value
            data["previous_response"] = coulson_output
            self.requeue_task(stream_id, data)
            self.sync_fastapi_state(ticket_id, TaskState.TESTING, {"coulson_audit": coulson_output})
            self.send_telegram_alert(ticket_id, "phil_coulson", TaskState.TESTING.value, coulson_output)
        else:
            logger.warning(f"[{ticket_id}] Coulson REJECTED. Delegating escalation to backend.")
            try:
                esc_req = {
                    "ticket_id": ticket_id,
                    "reason": "Rejected by Coulson",
                    "error_details": {"coulson_output": coulson_output, "exec_output": exec_output}
                }
                esc_url = self.fastapi_state_url.replace("update", "escalate")
                response = self.http_session.post(esc_url, json=esc_req, timeout=10)
                response.raise_for_status()
                esc_result = response.json()
                action = esc_result.get("action")
                
                if action == "FAILED_ESCALATED":
                    logger.error(f"[{ticket_id}] Backend escalated to FAILED_ESCALATED.")
                    
                    rocket_prompt = (
                        f"A ticket has been escalated by the backend.\\n\\n"
                        f"Ticket: {ticket_id}\\n"
                        f"Execution Output: {exec_output}\\n"
                        f"Coulson Audit Failure: {coulson_output}\\n\\n"
                        f"DIRECTIVE: Perform a root-cause diagnostic on this failure loop. Propose a permanent fix."
                    )
                    rocket_analysis = self.spawn_subagent("rocket_raccoon", rocket_prompt, ticket_id)
                    
                    self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {
                        "reason": "Backend escalated", 
                        "rocket_diagnostic": rocket_analysis
                    })
                    self.send_telegram_alert(ticket_id, "rocket_raccoon", TaskState.FAILED_ESCALATED.value, rocket_analysis)
                    self.ack_task(stream_id)
                else:
                    self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Re-queueing after rejection"})
                    data["status"] = TaskState.BUILDING.value
                    data["previous_response"] = f"PREVIOUS REJECTION REASON:\\n{coulson_output}"
                    self.requeue_task(stream_id, data)
                    self.send_telegram_alert(ticket_id, "phil_coulson", "REJECTED", coulson_output)
            except Exception as e:
                logger.error(f"Failed to call escalate endpoint: {e}")
                self.requeue_task(stream_id, data)"""

content = content.replace(old_logic, new_logic)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "w") as f:
    f.write(content)

print("Patched!")
