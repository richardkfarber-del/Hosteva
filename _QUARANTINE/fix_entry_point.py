import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'workflow.set_entry_point(' in line:
        lines[i] = line.replace('workflow.set_entry_point(', 'workflow.set_entry(')

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'w') as f:
    f.writelines(lines)
