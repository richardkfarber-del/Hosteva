import re

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "r") as f:
    content = f.read()

# Define the exact new Enum block
new_enum = """class TaskState(str, Enum):
    BACKLOG = "BACKLOG"
    REFINEMENT = "REFINEMENT"
    FAILED_REFINEMENT = "FAILED_REFINEMENT"
    BUILDING = "BUILDING"
    BLOCKED = "BLOCKED"
    AUDITING = "AUDITING"
    TESTING = "TESTING"
    REJECTED = "REJECTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    DEPLOYING = "DEPLOYING"
    DONE = "DONE"
    FAILED_ESCALATED = "FAILED_ESCALATED\""""

# We'll use a regex to replace the class definition
content = re.sub(r'class TaskState\(str, Enum\):.*?(?=\n\n|\Z)', new_enum, content, flags=re.DOTALL)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py", "w") as f:
    f.write(content)
