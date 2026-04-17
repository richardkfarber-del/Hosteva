import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

# Change coulson to phil_coulson where needed
content = content.replace('self.spawn_subagent("coulson"', 'self.spawn_subagent("phil_coulson"')

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)
