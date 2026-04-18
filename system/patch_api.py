with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/api/routes/swarm.py", "r") as f:
    content = f.read()

old_block = """    # Enforce State Transition
    if current_state in ALLOWED_TRANSITIONS and request.status not in ALLOWED_TRANSITIONS[current_state] and current_state != request.status:"""

new_block = """    # Enforce State Transition
    request.status = request.status.strip().upper()
    current_state = current_state.strip().upper()
    
    if current_state in ALLOWED_TRANSITIONS and request.status not in ALLOWED_TRANSITIONS[current_state] and current_state != request.status:"""

content = content.replace(old_block, new_block)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/api/routes/swarm.py", "w") as f:
    f.write(content)
