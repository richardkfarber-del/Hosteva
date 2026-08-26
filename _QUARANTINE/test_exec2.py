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
        # In GraphBit, if the execution returns immediately without doing anything,
        # maybe we need to pass a specific initial state to trigger the first node.
        # Or maybe it expects an initial message.
        pass
    except Exception as e:
        print('Error executing workflow:', e)
