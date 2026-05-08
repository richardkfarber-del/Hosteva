import json
import sys

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/03_planning_poker_artifact.md', 'r') as f:
    outputs = {'test': f.read()}

for k, v in outputs.items():
    if isinstance(v, str) and ('__KICKBACK__' in v.upper() or '__FAIL__' in v.upper()):
        print(f"Found in {k}")
        sys.exit(1)
print("Not found in artifact.")
