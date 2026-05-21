import sys
sys.path.append('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
import workflow

executor = workflow.Executor(workflow.local_config, timeout_seconds=3600)
res = executor.execute(workflow.workflow)
print(dir(res))
print(getattr(res, 'outputs', 'NO_OUTPUTS'))
print(getattr(res, 'state', 'NO_STATE'))
print(res)
