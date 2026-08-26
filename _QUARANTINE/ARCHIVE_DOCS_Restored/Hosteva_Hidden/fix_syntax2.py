with open("system/swarm_worker.py", "r") as f:
    content = f.read()

content = content.replace("prompt = f\"Refine this ticket for technical feasibility.\nTicket: {ticket_id}\nDesc: {task_desc}\nReply with JSON containing status 'BUILDING' or 'FAILED_REFINEMENT'.\"", 
                          "prompt = f\"\"\"Refine this ticket for technical feasibility.\\nTicket: {ticket_id}\\nDesc: {task_desc}\\nReply with JSON containing status 'BUILDING' or 'FAILED_REFINEMENT'.\"\"\"")

content = content.replace("prompt = f\"Run headless QA tests for Ticket: {ticket_id}. Requires PNG snapshot path.\nDesc: {task_desc}\nReply with JSON containing status 'VERIFIED' or 'REJECTED'.\"",
                          "prompt = f\"\"\"Run headless QA tests for Ticket: {ticket_id}. Requires PNG snapshot path.\\nDesc: {task_desc}\\nReply with JSON containing status 'VERIFIED' or 'REJECTED'.\"\"\"")

content = content.replace("prompt = f\"Deploy ticket {ticket_id} to production.\nDesc: {task_desc}\nReply with 'DEPLOY_SUCCESS' or 'DEPLOY_FAILED'.\"",
                          "prompt = f\"\"\"Deploy ticket {ticket_id} to production.\\nDesc: {task_desc}\\nReply with 'DEPLOY_SUCCESS' or 'DEPLOY_FAILED'.\"\"\"")

with open("system/swarm_worker.py", "w") as f:
    f.write(content)
