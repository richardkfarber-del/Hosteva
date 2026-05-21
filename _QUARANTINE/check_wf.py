import sys
sys.path.append('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
from workflow import workflow
try:
    workflow.validate()
    print("VALID")
except Exception as e:
    print("INVALID:", e)
