#!/usr/bin/env python3
import json, os, sys, subprocess
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(project_root, ".env"))

print("======================================================")
print("  [PHASE 8] DEPLOYMENT & INFRASTRUCTURE")
print("======================================================")

# 1. FORCE THE GIT COMMIT AND PUSH NATIVELY
print("-> Syncing local commits to remote GitHub repository...")
try:
    # Force add and commit any uncommitted changes (like Aider's fixes and the Dockerfile)
    subprocess.run(["git", "add", "."], cwd=project_root, check=True)
    subprocess.run(["git", "commit", "-m", "fix: Automated deployment sync - Uvicorn workers and Jinja2"], cwd=project_root)
except:
    pass # Ignore if there is nothing new to commit

try:
    # Force push current HEAD to remote main branch explicitly
    push_out = subprocess.check_output(["git", "push", "origin", "HEAD:main"], stderr=subprocess.STDOUT, text=True, cwd=project_root)
    print(f"[SUCCESS] Code pushed to GitHub:\n{push_out.strip()}")
except subprocess.CalledProcessError as e:
    print(f"\n[FATAL ERROR] Git Push Failed! Render will not have the updated code.\n{e.output}")
    sys.exit(1)

sys.path.append(project_root)
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config
from swarm_tools import submit_phase_plan, render_deploy, verify_render_deployment, run_shell_command

state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(project_root, "swarm_state.json"))
os.chdir(project_root)

try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

allowed_tools = [render_deploy, verify_render_deployment, run_shell_command, submit_phase_plan]

devops_directive = """
CRITICAL DEPLOYMENT DIRECTIVE:
The code has been successfully pushed to GitHub natively. You must now trigger the deployment and verify it goes live. DO NOT output multiple JSON blocks at once. Execute these EXACT tools one by one, waiting for the result of each before proceeding to the next.

STEP 1: Trigger the Render Deployment. Output EXACTLY this JSON:
{"name": "render_deploy", "arguments": {"service_id": "srv-d798m4chg0os73e3it70"}}

STEP 2: Wait for the result. Then, verify the deployment status. Output EXACTLY this JSON:
{"name": "verify_render_deployment", "arguments": {"service_id": "srv-d798m4chg0os73e3it70"}}

STEP 3: Wait for the result. 
- If the status is LIVE (GREEN), approve the deployment. Output EXACTLY this JSON:
{"name": "submit_phase_plan", "arguments": {"plan_markdown": "### [DEPLOYMENT APPROVED]"}}
- If the status is FAILED, you MUST reject the deployment. You may use the `run_shell_command` tool to investigate why it failed (e.g., checking logs) before rejecting.
"""

# Reset input to prevent hallucination loops from old directives
state["input"] = devops_directive

print("-> Executing Gate: Heimdall (deployment_infrastructure_skill.md)...")
result = run_single_agent("devops", "Heimdall", "deployment_infrastructure_skill.md", local_config, state, allowed_tools)
print(f"\n>>> [Heimdall OUTPUT]:\n{result}")

if result and "[DEPLOYMENT APPROVED]" in result:
    print("\n>>> [ORCHESTRATOR]: Phase 8 Complete. Live Deployment Successful.")
    state["current_phase"] = "09_uat"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)
    sys.exit(0)
else:
    print("\n>>> [ORCHESTRATOR]: 🔴 Deployment Failed or Rejected by Heimdall. Halting pipeline.")
    sys.exit(1)
