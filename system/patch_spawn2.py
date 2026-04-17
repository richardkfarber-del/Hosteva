import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

# Add the exception class
content = content.replace("class TaskState", "class FatalRosterError(Exception):\n    pass\n\nclass TaskState")

# Update the spawn_subagent method
new_logic = r"""def spawn_subagent(self, agent_id: str, prompt: str, ticket_id: str = "UNKNOWN") -> Optional[str]:
        # [SECURITY LOCK] Physical Roster Verification (Anti-Fragmentation)
        kebab_id = agent_id.replace('_', '-')
        agent_dir = f"/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/{kebab_id}"
        if not os.path.exists(agent_dir):
            error_msg = f"[CRITICAL ANOMALY] Attempted to spawn non-existent agent '{agent_id}'. Expected directory {agent_dir} is missing. Halting to prevent memory fragmentation."
            logger.critical(error_msg)
            # Escalate the ticket immediately
            if ticket_id != "UNKNOWN":
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {"reason": "Missing Agent Configuration", "error": error_msg})
            raise FatalRosterError(error_msg)

        if self._is_circuit_breaker_open():"""

content = re.sub(r'def spawn_subagent\(self, agent_id: str, prompt: str, ticket_id: str = "UNKNOWN"\) -> Optional\[str\]:.*?if self\._is_circuit_breaker_open\(\):', new_logic, content, flags=re.DOTALL)

# Add handling in run()
run_patch = r"""except FatalRosterError as fre:
                logger.critical(f"Pipeline Halting for Ticket {ticket_id}: {fre}")
                data["status"] = TaskState.FAILED_ESCALATED.value
                self.redis_client.rpush(self.dlq_name, json.dumps(data))
                # Alert the Secretary explicitly
                with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/CRITICAL_ALERT.txt", "w") as alert:
                    alert.write(f"DIRECTOR ALERT: A fragmented or non-existent agent ({ticket_id}) was requested. The daemon has executed a Hard Stop to prevent memory bleeding. Check DLQ.")
            except redis.exceptions.ConnectionError:"""

content = content.replace("except redis.exceptions.ConnectionError:", run_patch)

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)
