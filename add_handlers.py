with open("system/swarm_worker.py", "r") as f:
    content = f.read()

handlers = """
    def handle_backlog(self, data: Dict[str, Any], ticket_id: str, task_desc: str, stream_id: str) -> None:
        logger.info(f"[{ticket_id}] BACKLOG -> Transitioning to REFINEMENT")
        data["status"] = TaskState.REFINEMENT.value
        self.requeue_task(stream_id, data)
        self.sync_fastapi_state(ticket_id, TaskState.REFINEMENT, {"reason": "Auto-transition to refinement"})

    def handle_refinement(self, data: Dict[str, Any], ticket_id: str, task_desc: str, stream_id: str) -> None:
        logger.info(f"[{ticket_id}] REFINEMENT -> Spawning Hawkeye/Vision for feasibility")
        prompt = f"Refine this ticket for technical feasibility.\\nTicket: {ticket_id}\\nDesc: {task_desc}\\nReply with JSON containing status 'BUILDING' or 'FAILED_REFINEMENT'."
        output = self.spawn_subagent("vision", prompt, ticket_id)
        if output and "FAILED_REFINEMENT" in output:
            data["status"] = TaskState.FAILED_REFINEMENT.value
            self.sync_fastapi_state(ticket_id, TaskState.FAILED_REFINEMENT, {"reason": output})
        else:
            data["status"] = TaskState.BUILDING.value
            self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Refinement successful"})
        self.requeue_task(stream_id, data)

    def handle_testing(self, data: Dict[str, Any], ticket_id: str, task_desc: str, stream_id: str) -> None:
        logger.info(f"[{ticket_id}] TESTING -> Spawning Captain America")
        prompt = f"Run headless QA tests for Ticket: {ticket_id}. Requires PNG snapshot path.\\nDesc: {task_desc}\\nReply with JSON containing status 'VERIFIED' or 'REJECTED'."
        output = self.spawn_subagent("captain_america", prompt, ticket_id)
        if output and "REJECTED" in output:
            data["status"] = TaskState.REJECTED.value
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": output})
        else:
            data["status"] = TaskState.PENDING_APPROVAL.value
            self.sync_fastapi_state(ticket_id, TaskState.PENDING_APPROVAL, {"reason": "Testing passed, awaiting approval"})
        self.requeue_task(stream_id, data)

    def handle_deploying(self, data: Dict[str, Any], ticket_id: str, task_desc: str, stream_id: str) -> None:
        logger.info(f"[{ticket_id}] DEPLOYING -> Spawning Heimdall")
        prompt = f"Deploy ticket {ticket_id} to production.\\nDesc: {task_desc}\\nReply with 'DEPLOY_SUCCESS' or 'DEPLOY_FAILED'."
        output = self.spawn_subagent("heimdall", prompt, ticket_id)
        if output and "DEPLOY_SUCCESS" in output:
            data["status"] = TaskState.DONE.value
            self.sync_fastapi_state(ticket_id, TaskState.DONE, {"reason": "Deployment successful"})
            self.send_telegram_alert(ticket_id, "heimdall", TaskState.DONE.value, "Deployment successful")
            self.ack_task(stream_id)
        else:
            data["status"] = TaskState.REJECTED.value
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": "Deployment failed"})
            self.requeue_task(stream_id, data)

"""

import re
# Insert handlers before handle_building
content = re.sub(r'    def handle_building\(', handlers + r'\n    def handle_building(', content)

with open("system/swarm_worker.py", "w") as f:
    f.write(content)
