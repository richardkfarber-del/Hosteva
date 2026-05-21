import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'r') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if line.startswith('    ') and 'Node.agent(' in line:
        lines[i] = line[4:] # remove indent

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'w') as f:
    f.write('\n'.join(lines))
