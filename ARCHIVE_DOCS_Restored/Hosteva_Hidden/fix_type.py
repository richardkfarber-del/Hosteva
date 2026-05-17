import sys

file_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_workflow.py"
with open(file_path, "r") as f:
    content = f.read()

old_block = """        # Phase 6: Evolution Loop / Deep Write (Exec Review)
        await workflow.execute_activity(
            evolution_loop_deep_write,
            evolution_loop_deep_write,
            deploy_status,
            start_to_close_timeout=timedelta(minutes=5),
        )"""

new_block = """        # Phase 6: Evolution Loop / Deep Write (Exec Review)
        await workflow.execute_activity(
            evolution_loop_deep_write,
            deploy_status,
            start_to_close_timeout=timedelta(minutes=5),
        )"""

content = content.replace(old_block, new_block)

with open(file_path, "w") as f:
    f.write(content)
