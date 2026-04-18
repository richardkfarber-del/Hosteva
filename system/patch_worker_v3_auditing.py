import sys

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

handle_auditing_old = """        coulson_output = self.spawn_subagent("phil_coulson", coulson_prompt, ticket_id)
        
        if not coulson_output:
            logger.warning(f"[{ticket_id}] Transient Gateway failure during QA. Re-queueing AUDITING. No strike burned.")
            time.sleep(5)
            self.requeue_task(stream_id, data)
            return"""

handle_auditing_new = """        coulson_output = self.spawn_subagent("phil_coulson", coulson_prompt, ticket_id)
        
        if not coulson_output:
            self.handle_spawn_failure(data, ticket_id, stream_id, "phil_coulson")
            return
        self.redis_client.delete(f"swarm:routing_strikes:{ticket_id}")"""

if handle_auditing_old in content:
    content = content.replace(handle_auditing_old, handle_auditing_new)

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)

print("Auditing patch appended.")
