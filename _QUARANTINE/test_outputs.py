import sys
sys.path.append('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
import workflow

executor = workflow.Executor(workflow.local_config, timeout_seconds=3600)
res = executor.execute(workflow.workflow)
print('Execution time:', res.execution_time_ms())
print('Success:', res.is_success())
print('Failed:', res.is_failed())
print('Node outputs:', res.get_all_node_outputs())
print('Variables:', res.get_all_variables())
