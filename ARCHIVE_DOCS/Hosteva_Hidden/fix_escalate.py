with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "r") as f:
    content = f.read()

# Add FAILED_ESCALATED to TaskState enum
if "FAILED_ESCALATED" not in content:
    content = content.replace("DONE = \"DONE\"", "DONE = \"DONE\"\n    FAILED_ESCALATED = \"FAILED_ESCALATED\"")

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "w") as f:
    f.write(content)
