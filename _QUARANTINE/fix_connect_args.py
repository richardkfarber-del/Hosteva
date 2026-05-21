import os

path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py'
with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'workflow.connect(' in line and ', [' in line:
        # e.g. workflow.connect(ids['Hawkeye'], ids['Hawkeye Router'], [ids['Vision'], ids['Hulk']])
        # we just want to keep the first two arguments.
        parts = line.split(', [')
        new_line = parts[0] + ')\n'
        new_lines.append(new_line)
    else:
        new_lines.append(line)

with open(path, 'w') as f:
    f.writelines(new_lines)
