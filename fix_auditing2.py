import re

with open('system/swarm_worker.py', 'r') as f:
    content = f.read()

pattern = r'''    def handle_auditing\(self, data: Dict\[str, Any\], ticket_id: str, stream_id: str\) -> None:
        self\.sync_fastapi_state\(ticket_id, TaskState\.AUDITING, \{"reason": "Executing phase"\}\)
        logger\.info\(f"\[\{ticket_id\}\] Routing to Coulson Tollbooth for physical verification\.\.\."\)
        exec_output = data\.get\("previous_response", "No output provided\."\)
        
        ticket_reqs = self\._extract_ticket_requirements\(ticket_id\)
        
        coulson_prompt = \(.*?\)'''

replacement = r'''    def handle_auditing(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] Routing to Coulson Tollbooth for physical verification...")
        exec_output = data.get("previous_response", "No output provided.")
        
        ticket_reqs = self._extract_ticket_requirements(ticket_id)
        
        coulson_prompt = (
            f"Audit this execution for {ticket_id}:\n\n"
            f"TICKET_REQUIREMENTS:\n{ticket_reqs}\n\n"
            f"Execution Squad Output:\n{exec_output}\n\n"
            f"DIRECTIVE: Verify physical reality. Check file paths, hashes, or run tests. "
            f"You MUST reply with a strict JSON object containing a 'status' key set to exactly 'VERIFIED' or 'REJECTED'. "
            f"If rejected, include a 'reason' key. Example: {{\"status\": \"VERIFIED\"}} or {{\"status\": \"REJECTED\", \"reason\": \"<explicit reasoning>\"}}"
        )'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('system/swarm_worker.py', 'w') as f:
    f.write(content)
