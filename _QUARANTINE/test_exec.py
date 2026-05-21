import os
from dotenv import load_dotenv
load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
import sys
sys.path.append('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
import workflow

if __name__ == '__main__':
    print("Starting executor test...")
    executor = workflow.Executor(workflow.local_config, timeout_seconds=3600)
    try:
        final_state = executor.execute(workflow.workflow)
        print('Workflow executed successfully. Final state:', final_state)
    except Exception as e:
        print('Error executing workflow:', e)
