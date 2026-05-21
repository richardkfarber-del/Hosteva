import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('ids = {n.name:'):
        lines[i] = "ids = {n.name: workflow.add_node(n) for n in nodes}\n"
        # The previous code used n.name, which works if the objects have a .name attribute.
        # Let's verify what the actual names are.

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'w') as f:
    f.writelines(lines)
