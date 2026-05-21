import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('ids = {n.name:'):
        # n.name is a method, so we need n.name() or we can extract the name from the nodes list
        lines[i] = "ids = {n.name(): workflow.add_node(n) for n in nodes}\n"

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'w') as f:
    f.writelines(lines)
