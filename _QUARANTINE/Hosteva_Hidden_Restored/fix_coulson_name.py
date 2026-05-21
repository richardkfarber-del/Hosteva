with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "r") as f:
    content = f.read()

# Fix the agent name spawn call
content = content.replace('coulson_output = self.spawn_subagent("phil_coulson", coulson_prompt, ticket_id)', 'coulson_output = self.spawn_subagent("phil_coulson", coulson_prompt, ticket_id)')

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "w") as f:
    f.write(content)
