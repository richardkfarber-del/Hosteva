import sys

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "r") as f:
    content = f.read()

old_logic = """    def handle_spawn_failure(self, data: Dict[str, Any], ticket_id: str, stream_id: str, agent_name: str) -> None:
        retry_key = f"swarm:routing_strikes:{ticket_id}"
        retry_count = self.redis_client.incr(retry_key)
        
        if retry_count >= 3:
            logger.error(f"[{ticket_id}] 3-Strike Limit Hit for routing/gateway failures. Escalating to FAILED_ESCALATED.")
            data["status"] = TaskState.FAILED_ESCALATED.value
            self.redis_client.delete(retry_key)
            self.dlq_task(stream_id, data)
            self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {"reason": f"Failed to route/spawn agent {agent_name} after 3 attempts. Gateway might be down."})
            self.send_telegram_alert(ticket_id, agent_name, TaskState.FAILED_ESCALATED.value, "Gateway routing failure - 3 strikes.")
        else:
            backoff = min(120, 5 ** retry_count)
            logger.error(f"[{ticket_id}] Execution failed for {agent_name}. Strike {retry_count}/3. Re-queueing with {backoff}s backoff.")
            time.sleep(backoff)
            self.requeue_task(stream_id, data)"""

new_logic = """    def handle_spawn_failure(self, data: Dict[str, Any], ticket_id: str, stream_id: str, agent_name: str) -> None:
        try:
            esc_req = {
                "ticket_id": ticket_id,
                "reason": f"Failed to route/spawn agent {agent_name}. Gateway might be down.",
                "error_details": {"agent_name": agent_name}
            }
            esc_url = self.fastapi_state_url.replace("update", "escalate")
            response = self.http_session.post(esc_url, json=esc_req, timeout=10)
            response.raise_for_status()
            esc_result = response.json()
            action = esc_result.get("action")
            
            if action == "FAILED_ESCALATED":
                logger.error(f"[{ticket_id}] Backend escalated routing failure to FAILED_ESCALATED.")
                self.send_telegram_alert(ticket_id, agent_name, TaskState.FAILED_ESCALATED.value, "Gateway routing failure - escalated by backend.")
                self.ack_task(stream_id)
            else:
                retry_count = esc_result.get("strikes", 1)
                backoff = min(120, 5 ** retry_count)
                logger.error(f"[{ticket_id}] Execution failed for {agent_name}. Strike {retry_count}/3. Re-queueing with {backoff}s backoff.")
                time.sleep(backoff)
                self.requeue_task(stream_id, data)
        except Exception as e:
            logger.error(f"Failed to call escalate endpoint for routing failure: {e}")
            time.sleep(5)
            self.requeue_task(stream_id, data)"""

content = content.replace(old_logic, new_logic)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "w") as f:
    f.write(content)

print("Patched routing!")
