import sys
sys.path.insert(0, '/home/rdogen/OpenClaw_Factory/projects/Hosteva')
import workflow

try:
    workflow.workflow.validate()
    print('Validation passed')
except Exception as e:
    print('Validation error:', e)
