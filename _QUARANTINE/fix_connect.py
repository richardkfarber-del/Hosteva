import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'workflow.connect(' in line and '[' in line and ']' in line:
        # E.g. workflow.connect(ids['Hawkeye'], ids['Hawkeye Router'], ['Vision', 'Hulk'])
        # The GraphBit Python binding doesn't support the 3rd argument for targets.
        # We need to strip it out.
        m = re.match(r"(workflow\.connect\([^,]+,\s*[^,]+\)),\s*\[.*\]\)", line)
        if m:
            lines[i] = m.group(1) + ")\n"

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py', 'w') as f:
    f.writelines(lines)
