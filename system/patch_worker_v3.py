import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

# 1. Add FAILED_ESCALATED to TaskState
content = content.replace(
    '    DONE = "DONE"',
    '    DONE = "DONE"\n    FAILED_ESCALATED = "FAILED_ESCALATED"'
)

# 2. Add handle_spawn_failure method
handle_spawn_failure_code = """
    def handle_spawn_failure(self, data: Dict[str, Any], ticket_id: str, stream_id: str, agent_name: str) -> None:
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
            self.requeue_task(stream_id, data)

"""

if "def handle_spawn_failure" not in content:
    content = content.replace(
        '    def handle_backlog(',
        handle_spawn_failure_code + '    def handle_backlog('
    )

# 3. Update handle_building
handle_building_old = """        if exec_output:
            interceptor_error = self.verify_execution_output(exec_output, ticket_id)
            if interceptor_error:
                logger.info(f"[{ticket_id}] Interceptor VETO. Re-queueing as BUILDING.")
                data["status"] = TaskState.BUILDING.value
                data["previous_response"] = f"Execution VETOED by Courier:\\n{interceptor_error}\\n\\nPlease try again and actually write the files."
                self.requeue_task(stream_id, data)
                self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Interceptor Veto"})
            else:
                data["status"] = TaskState.AUDITING.value
                data["previous_response"] = exec_output
                self.requeue_task(stream_id, data)
                self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"previous_response": exec_output})
        else:
            logger.error(f"[{ticket_id}] Execution failed. Re-queueing as PENDING.")
            time.sleep(5)
            self.requeue_task(stream_id, data)"""

handle_building_new = """        if exec_output:
            self.redis_client.delete(f"swarm:routing_strikes:{ticket_id}")
            interceptor_error = self.verify_execution_output(exec_output, ticket_id)
            if interceptor_error:
                logger.info(f"[{ticket_id}] Interceptor VETO. Re-queueing as BUILDING.")
                data["status"] = TaskState.BUILDING.value
                data["previous_response"] = f"Execution VETOED by Courier:\\n{interceptor_error}\\n\\nPlease try again and actually write the files."
                self.requeue_task(stream_id, data)
                self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Interceptor Veto"})
            else:
                data["status"] = TaskState.AUDITING.value
                data["previous_response"] = exec_output
                self.requeue_task(stream_id, data)
                self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"previous_response": exec_output})
        else:
            self.handle_spawn_failure(data, ticket_id, stream_id, assigned_agent)"""

content = content.replace(handle_building_old, handle_building_new)

# 4. Update handle_refinement
handle_refinement_old = """        output = self.spawn_subagent("vision", prompt, ticket_id)
        if output and "FAILED_REFINEMENT" in output:
            data["status"] = TaskState.FAILED_REFINEMENT.value
            self.sync_fastapi_state(ticket_id, TaskState.FAILED_REFINEMENT, {"reason": output})
            self.send_telegram_alert(ticket_id, "vision", TaskState.FAILED_REFINEMENT.value, output)
        else:
            data["status"] = TaskState.BUILDING.value
            self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Refinement successful"})
        self.requeue_task(stream_id, data)"""

handle_refinement_new = """        output = self.spawn_subagent("vision", prompt, ticket_id)
        if not output:
            self.handle_spawn_failure(data, ticket_id, stream_id, "vision")
            return
        self.redis_client.delete(f"swarm:routing_strikes:{ticket_id}")
        if "FAILED_REFINEMENT" in output:
            data["status"] = TaskState.FAILED_REFINEMENT.value
            self.sync_fastapi_state(ticket_id, TaskState.FAILED_REFINEMENT, {"reason": output})
            self.send_telegram_alert(ticket_id, "vision", TaskState.FAILED_REFINEMENT.value, output)
        else:
            data["status"] = TaskState.BUILDING.value
            self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Refinement successful"})
        self.requeue_task(stream_id, data)"""

content = content.replace(handle_refinement_old, handle_refinement_new)

# 5. Update handle_testing
handle_testing_old = """        output = self.spawn_subagent("captain_america", prompt, ticket_id)
        if output and "REJECTED" in output:
            data["status"] = TaskState.REJECTED.value
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": output})
        else:
            data["status"] = TaskState.PENDING_APPROVAL.value
            self.sync_fastapi_state(ticket_id, TaskState.PENDING_APPROVAL, {"reason": "Testing passed, awaiting approval"})
        self.requeue_task(stream_id, data)"""

handle_testing_new = """        output = self.spawn_subagent("captain_america", prompt, ticket_id)
        if not output:
            self.handle_spawn_failure(data, ticket_id, stream_id, "captain_america")
            return
        self.redis_client.delete(f"swarm:routing_strikes:{ticket_id}")
        if "REJECTED" in output:
            data["status"] = TaskState.REJECTED.value
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": output})
        else:
            data["status"] = TaskState.PENDING_APPROVAL.value
            self.sync_fastapi_state(ticket_id, TaskState.PENDING_APPROVAL, {"reason": "Testing passed, awaiting approval"})
        self.requeue_task(stream_id, data)"""

content = content.replace(handle_testing_old, handle_testing_new)

# 6. Update handle_deploying
handle_deploying_old = """        output = self.spawn_subagent("heimdall", prompt, ticket_id)
        if output and "DEPLOY_SUCCESS" in output:
            data["status"] = TaskState.DONE.value
            self.sync_fastapi_state(ticket_id, TaskState.DONE, {"reason": "Deployment successful"})
            self.send_telegram_alert(ticket_id, "heimdall", TaskState.DONE.value, "Deployment successful")
            self.ack_task(stream_id)
        else:
            data["status"] = TaskState.REJECTED.value
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": "Deployment failed"})
            self.requeue_task(stream_id, data)"""

handle_deploying_new = """        output = self.spawn_subagent("heimdall", prompt, ticket_id)
        if not output:
            self.handle_spawn_failure(data, ticket_id, stream_id, "heimdall")
            return
        self.redis_client.delete(f"swarm:routing_strikes:{ticket_id}")
        if "DEPLOY_SUCCESS" in output:
            data["status"] = TaskState.DONE.value
            self.sync_fastapi_state(ticket_id, TaskState.DONE, {"reason": "Deployment successful"})
            self.send_telegram_alert(ticket_id, "heimdall", TaskState.DONE.value, "Deployment successful")
            self.ack_task(stream_id)
        else:
            data["status"] = TaskState.REJECTED.value
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": "Deployment failed"})
            self.requeue_task(stream_id, data)"""

content = content.replace(handle_deploying_old, handle_deploying_new)


with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)

print("Patch applied successfully.")
