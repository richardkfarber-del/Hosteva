import re

with open('system/swarm_worker.py', 'r') as f:
    content = f.read()

helper_function = """
    def _extract_ticket_requirements(self, ticket_id: str) -> str:
        try:
            with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md", "r") as f:
                content = f.read()
            
            ticket_marker = f"### {ticket_id}"
            if ticket_marker not in content:
                return f"No requirements found for {ticket_id}."
            
            start_index = content.find(ticket_marker)
            next_ticket_index = content.find("### ", start_index + len(ticket_marker))
            
            if next_ticket_index == -1:
                return content[start_index:]
            else:
                return content[start_index:next_ticket_index]
        except Exception as e:
            return f"Error reading requirements for {ticket_id}: {e}"

    def handle_backlog"""

content = content.replace("    def handle_backlog", helper_function)


old_handle_testing = """    def handle_testing(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.TESTING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] TESTING -> Spawning Captain America")
        prompt = f"Run headless QA tests for Ticket: {ticket_id}. Requires PNG snapshot path.\\nUse your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\\nReply with JSON containing status 'VERIFIED' or 'REJECTED'."
        output = self.spawn_subagent("captain_america", prompt, ticket_id)"""

new_handle_testing = """    def handle_testing(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.TESTING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] TESTING -> Spawning Captain America")
        
        ticket_reqs = self._extract_ticket_requirements(ticket_id)
        
        prompt = f"Run headless QA tests for Ticket: {ticket_id}. Requires PNG snapshot path.\\n\\nTICKET_REQUIREMENTS:\\n{ticket_reqs}\\n\\nReply with JSON containing status 'VERIFIED' or 'REJECTED'."
        output = self.spawn_subagent("captain_america", prompt, ticket_id)"""

content = content.replace(old_handle_testing, new_handle_testing)


old_handle_auditing = """    def handle_auditing(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] Routing to Coulson Tollbooth for physical verification...")
        exec_output = data.get("previous_response", "No output provided.")
        
        coulson_prompt = (
            f"Audit this execution for {ticket_id}:\\n\\n"
            f"Use your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\\n\\n"
            f"Execution Squad Output:\\n{exec_output}\\n\\n"
            f"DIRECTIVE: Verify physical reality. Check file paths, hashes, or run tests. "
            f"You MUST reply with a strict JSON object containing a 'status' key set to exactly 'VERIFIED' or 'REJECTED'. "
            f"If rejected, include a 'reason' key. Example: {{\\"status\\": \\"VERIFIED\\"}} or {{\\"status\\": \\"REJECTED\\", \\"reason\\": \\"<explicit reasoning>\\"}}\\n"
            f"SPRINT 11 HALLUCINATION PROTOCOL: You MUST use your tools to physically read 'project_board.md' to retrieve the actual Acceptance Criteria before generating your audit. DO NOT hallucinate the ticket requirements."
        )"""

new_handle_auditing = """    def handle_auditing(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] Routing to Coulson Tollbooth for physical verification...")
        exec_output = data.get("previous_response", "No output provided.")
        
        ticket_reqs = self._extract_ticket_requirements(ticket_id)
        
        coulson_prompt = (
            f"Audit this execution for {ticket_id}:\\n\\n"
            f"TICKET_REQUIREMENTS:\\n{ticket_reqs}\\n\\n"
            f"Execution Squad Output:\\n{exec_output}\\n\\n"
            f"DIRECTIVE: Verify physical reality. Check file paths, hashes, or run tests. "
            f"You MUST reply with a strict JSON object containing a 'status' key set to exactly 'VERIFIED' or 'REJECTED'. "
            f"If rejected, include a 'reason' key. Example: {{\\"status\\": \\"VERIFIED\\"}} or {{\\"status\\": \\"REJECTED\\", \\"reason\\": \\"<explicit reasoning>\\"}}"
        )"""

content = content.replace(old_handle_auditing, new_handle_auditing)

with open('system/swarm_worker.py', 'w') as f:
    f.write(content)

