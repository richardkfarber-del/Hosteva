filepath = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py"
with open(filepath, 'r') as f:
    content = f.read()

old_prompt = """prompt = f"Deploy ticket {ticket_id} locally.\\nUse your tools to read /home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md, find your specific ticket_id, and extract your requirements.\\nV3.0 PIPELINE OVERRIDE: Execute your Dual-Path Deployment Doctrine (Path B) for local internal tooling. Verify the Git staging area (`git diff --staged`) and formally execute `git commit -m \\"[{ticket_id}] Deployment Approved\\"` to merge the code. Do NOT search for Render configurations or execute deploy_to_render.sh. If the merge is successful and the staging area is clean, reply exactly with 'DEPLOY_SUCCESS'. If it fails, reply exactly with 'DEPLOY_FAILED' followed by your detailed error trace." """

new_prompt = """prompt = f"Deploy ticket {ticket_id} locally.\\nUse your tools to read /home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md, find your specific ticket_id, and extract your requirements.\\nV3.0 PIPELINE OVERRIDE: Execute your Dual-Path Deployment Doctrine (Path B) for local internal tooling. You are the final CI/CD Gatekeeper.\\n1. Use `git diff --staged` to rigorously review the physical code changes.\\n2. Verify the changes mathematically satisfy the Acceptance Criteria on the board.\\n3. Check for any obvious syntax regressions or file permission errors.\\n4. Only if the code is pristine, formally execute `git commit -m \\"[{ticket_id}] Deployment Approved\\"` to merge the code.\\nDo NOT search for Render configurations or execute deploy_to_render.sh. If the merge is successful and the staging area is clean, reply exactly with 'DEPLOY_SUCCESS'. If the code fails your review or the merge fails, reply exactly with 'DEPLOY_FAILED' followed by your detailed error trace." """

if old_prompt.strip() in content:
    content = content.replace(old_prompt.strip(), new_prompt.strip())
    with open(filepath, 'w') as f:
        f.write(content)
    print("Refined prompt applied.")
else:
    print("Could not find the target string to patch.")
