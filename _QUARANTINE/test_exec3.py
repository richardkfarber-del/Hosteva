import sys
import os
sys.path.append('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
import workflow

executor = workflow.Executor(workflow.local_config, timeout_seconds=3600)
initial_state = {'node_outputs': {}, 'messages': [{'role': 'user', 'content': 'Please start the sprint.'}]}

# The executor might need the state passed in execute()
import inspect
print(inspect.signature(executor.execute))
