with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/api/routes/swarm.py", "r") as f:
    content = f.read()

old_matrix = """ALLOWED_TRANSITIONS = {
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

new_matrix = """ALLOWED_TRANSITIONS = {
    "BACKLOG": ["REFINEMENT", "BLOCKED"],
    "REFINEMENT": ["BUILDING", "FAILED_REFINEMENT", "BLOCKED"],
    "FAILED_REFINEMENT": ["BACKLOG", "REFINEMENT"],
    "BUILDING": ["AUDITING", "BLOCKED"],
    "BLOCKED": ["BACKLOG", "REFINEMENT", "BUILDING", "DEPLOYING"],
    "AUDITING": ["TESTING", "REJECTED", "BLOCKED", "FAILED_ESCALATED"],
    "TESTING": ["PENDING_APPROVAL", "REJECTED", "BLOCKED"],
    "REJECTED": ["BUILDING", "BLOCKED"],
    "FAILED_ESCALATED": ["BACKLOG", "BUILDING"],
    "PENDING_APPROVAL": ["DEPLOYING", "REJECTED"],
    "DEPLOYING": ["DONE", "REJECTED"],
    "DONE": []
}"""

content = content.replace(old_matrix, new_matrix)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/api/routes/swarm.py", "w") as f:
    f.write(content)
