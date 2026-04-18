import re

with open("app/api/routes/swarm.py", "r") as f:
    content = f.read()

# Replace ALLOWED_TRANSITIONS
new_transitions = """ALLOWED_TRANSITIONS = {
    "BACKLOG": ["REFINEMENT", "BLOCKED"],
    "REFINEMENT": ["BUILDING", "FAILED_REFINEMENT", "BLOCKED"],
    "FAILED_REFINEMENT": ["BACKLOG", "REFINEMENT"],
    "BUILDING": ["AUDITING", "BLOCKED"],
    "BLOCKED": ["BACKLOG", "REFINEMENT", "BUILDING", "DEPLOYING"],
    "AUDITING": ["TESTING", "REJECTED", "BLOCKED"],
    "TESTING": ["PENDING_APPROVAL", "REJECTED", "BLOCKED"],
    "REJECTED": ["BUILDING", "BLOCKED"],
    "PENDING_APPROVAL": ["DEPLOYING", "REJECTED"],
    "DEPLOYING": ["DONE", "REJECTED"],
    "DONE": []
}"""

content = re.sub(r'ALLOWED_TRANSITIONS\s*=\s*\{.*?\n\}', new_transitions, content, flags=re.DOTALL)

# Adjust DREAMSTATE logic
dreamstate_logic = """    if request.status == "PENDING_APPROVAL":
        if not request.payload or "security_audit" not in request.payload:
            pass # We might just alert director
"""
content = re.sub(r'    if request.status == "DREAMSTATE_READY":.*?(?=    await redis_client\.set)', dreamstate_logic, content, flags=re.DOTALL)

# Default state PENDING -> BACKLOG
content = content.replace('"PENDING"', '"BACKLOG"')

with open("app/api/routes/swarm.py", "w") as f:
    f.write(content)
