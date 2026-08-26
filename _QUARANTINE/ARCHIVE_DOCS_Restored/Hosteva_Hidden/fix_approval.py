with open("system/swarm_worker.py", "r") as f:
    content = f.read()

content = content.replace("TaskState.BACKLOG_APPROVAL", "TaskState.PENDING_APPROVAL")

with open("system/swarm_worker.py", "w") as f:
    f.write(content)
