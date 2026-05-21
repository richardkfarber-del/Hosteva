import json
import sys

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/03_planning_poker_artifact.md', 'r') as f:
    content = f.read()

if '__KICKBACK__' in content.upper() or '__FAIL__' in content.upper():
    print("Found in upper content")
else:
    print("Not found in upper content")
