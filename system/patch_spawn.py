import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

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
                # We return a specific failure token to abort the flow
            return "[ANOMALY] Agent does not exist."

        if self._is_circuit_breaker_open():"""

# Find the signature
content = re.sub(r'def spawn_subagent\(self, agent_id: str, prompt: str\) -> Optional\[str\]:\n\s+""".*?"""\n\s+if self\._is_circuit_breaker_open\(\):', new_logic, content, flags=re.DOTALL)

# We also need to update the calls to pass ticket_id for better error reporting
content = re.sub(r'self\.spawn_subagent\("jarvis", jarvis_prompt\)', r'self.spawn_subagent("jarvis", jarvis_prompt, ticket_id)', content)
content = re.sub(r'self\.spawn_subagent\(assigned_agent, agent_prompt\)', r'self.spawn_subagent(assigned_agent, agent_prompt, ticket_id)', content)
content = re.sub(r'self\.spawn_subagent\("coulson", coulson_prompt\)', r'self.spawn_subagent("coulson", coulson_prompt, ticket_id)', content)
content = re.sub(r'self\.spawn_subagent\("rocket_raccoon", rocket_prompt\)', r'self.spawn_subagent("rocket_raccoon", rocket_prompt, ticket_id)', content)


with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)
