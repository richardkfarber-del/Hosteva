import sys

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPRINT_BACKLOG.md', 'r') as f:
    content = f.read()

content = content.replace('**STATUS: SPRINT IN PROGRESS**', '**STATUS: EXECUTIVE SIGN-OFF GRANTED**')

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPRINT_BACKLOG.md', 'w') as f:
    f.write(content)
