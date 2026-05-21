import re

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/api/routes/swarm.py", "r") as f:
    content = f.read()

new_endpoint = """
@router.post("/submit")
async def submit_task(request: StateUpdateRequest, redis_client=Depends(get_redis)):
    data = request.model_dump()
    await redis_client.xadd("swarm:stream:tasks", {"payload": json.dumps(data)})
    return {"status": "success", "ticket_id": request.ticket_id}
"""

if "/submit" not in content:
    content += new_endpoint
    with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/app/api/routes/swarm.py", "w") as f:
        f.write(content)
