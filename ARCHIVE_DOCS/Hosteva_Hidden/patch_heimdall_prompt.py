filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py"
with open(filepath, 'r') as f:
    content = f.read()

old_prompt_code = """prompt = f\"\"\"Deploy ticket {ticket_id} to production.\\nUse your tools to read /home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md, find your specific ticket_id, and extract your requirements.\\nV3.0 PIPELINE OVERRIDE: Legacy `state.json` is deprecated. Executive Approval verified.\\nPHYSICAL DEPLOYMENT MANDATE: You MUST physically execute the following command using your exec tool:\\n`/home/rdogen/OpenClaw_Factory/projects/Hosteva/scripts/deploy_to_render.sh {ticket_id}`\\nYou MUST wait for the tool to finish. Do NOT hallucinate the result. If the script outputs 'DEPLOYMENT_VERIFIED', then you reply exactly with 'DEPLOY_SUCCESS'. If it fails, reply with 'DEPLOY_FAILED'.\"\"\""""

new_prompt_code = """
        if ticket_id.startswith(("CHORE-", "BUG-")):
            prompt = f"Deploy ticket {ticket_id} locally.\\nUse your tools to read /home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md, find your specific ticket_id, and extract your requirements.\\nV3.0 PIPELINE OVERRIDE: Execute your Dual-Path Deployment Doctrine (Path B) for local internal tooling. Verify the Git staging area (`git diff --staged`) and formally execute `git commit -m \\"[{ticket_id}] Deployment Approved\\"` to merge the code. Do NOT search for Render configurations or execute deploy_to_render.sh. If the merge is successful and the staging area is clean, reply exactly with 'DEPLOY_SUCCESS'. If it fails, reply exactly with 'DEPLOY_FAILED' followed by your detailed error trace."
        else:
            prompt = f\"\"\"Deploy ticket {ticket_id} to production.\\nUse your tools to read /home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md, find your specific ticket_id, and extract your requirements.\\nV3.0 PIPELINE OVERRIDE: Execute your Dual-Path Deployment Doctrine (Path A) for Hosteva App Cloud Deployment.\\nPHYSICAL DEPLOYMENT MANDATE: You MUST physically execute the following command using your exec tool:\\n`/home/rdogen/OpenClaw_Factory/projects/Hosteva/scripts/deploy_to_render.sh {ticket_id}`\\nYou MUST wait for the tool to finish. Do NOT hallucinate the result. If the script outputs 'DEPLOYMENT_VERIFIED', then you reply exactly with 'DEPLOY_SUCCESS'. If it fails, reply with 'DEPLOY_FAILED' followed by your detailed error trace.\"\"\"
"""

if old_prompt_code in content:
    content = content.replace(old_prompt_code, new_prompt_code.strip())
    with open(filepath, 'w') as f:
        f.write(content)
    print("Patch applied successfully.")
else:
    print("Could not find the target string to patch.")
