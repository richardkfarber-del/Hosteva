import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

new_routing = """        assigned_agent = "iron_man" # Default
        task_desc_lower = task_desc.lower()
        if "frontend" in task_desc_lower or "wasp" in task_desc_lower:
            assigned_agent = "wasp"
        elif "ant-man" in task_desc_lower:
            assigned_agent = "ant_man"
        elif "shang-chi" in task_desc_lower:
            assigned_agent = "shang_chi"
        elif "heimdall" in task_desc_lower or "deploy" in task_desc_lower:
            assigned_agent = "heimdall"
        elif "captain america" in task_desc_lower or "qa" in task_desc_lower or "uat" in task_desc_lower:
            assigned_agent = "captain_america"
        elif "wanda" in task_desc_lower or "scarlet witch" in task_desc_lower or "retro" in task_desc_lower or "deep write" in task_desc_lower:
            assigned_agent = "scarlet_witch"
"""

content = re.sub(r'        assigned_agent = "iron_man" # Default\n.*?assigned_agent = "shang_chi"', new_routing, content, flags=re.DOTALL)

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)
