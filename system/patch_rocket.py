import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

new_logic = r"""if retry_count >= 3:
                logger.error(f"[{ticket_id}] 3-Strike Limit Hit. Escalating to Rocket Raccoon.")
                
                rocket_prompt = (
                    f"A ticket has failed 3 consecutive times.\\n\\n"
                    f"Ticket: {ticket_id}\\n"
                    f"Task: {task_desc}\\n"
                    f"Execution Output: {exec_output}\\n"
                    f"Coulson Audit Failure: {coulson_output}\\n\\n"
                    f"DIRECTIVE: Perform a root-cause diagnostic on this failure loop. Propose a permanent fix. Do not write the code. Output your recommendation for the Secretary's review."
                )
                
                rocket_analysis = self.spawn_subagent("rocket_raccoon", rocket_prompt)
                
                data["status"] = TaskState.FAILED_ESCALATED.value
                self.redis_client.rpush(self.dlq_name, json.dumps(data))
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {
                    "reason": "3 strikes hit", 
                    "last_audit": coulson_output,
                    "rocket_diagnostic": rocket_analysis
                })"""

content = re.sub(r'if retry_count >= 3:.*?rocket_diagnostic": rocket_analysis\n                \}\)', new_logic, content, flags=re.DOTALL)

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)
