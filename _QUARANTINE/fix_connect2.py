import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'workflow.connect(' in line and '[' in line and ']' in line:
        # E.g. workflow.connect(ids['Hawkeye'], ids['Hawkeye Router'], ['Vision', 'Hulk'])
        # We need to strip the list argument.
        line = re.sub(r",\s*\[.*?\]\)", ")", line)
        lines[i] = line

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'w') as f:
    f.writelines(lines)
