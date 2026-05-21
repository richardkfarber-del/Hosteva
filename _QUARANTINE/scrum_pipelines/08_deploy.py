#!/usr/bin/env python3
import json, os, sys, subprocess
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
project_root = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(project_root, ".env"))

sys.path.append(project_root)
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config
from swarm_tools import submit_phase_plan, docker_build, render_deploy, verify_render_deployment, get_render_logs

print("======================================================")
print("  [PHASE 8] DEPLOYMENT & INFRASTRUCTURE")
print("======================================================")

state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(project_root, "swarm_state.json"))
os.chdir(project_root)

try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

try:
    diff_raw = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True)
    diff_output = diff_raw[:1500] + "\n...[DIFF TRUNCATED TO SAVE LLM CONTEXT TOKENS]..."
except:
    diff_output = "No diff available."

allowed_tools = [docker_build, render_deploy, verify_render_deployment, get_render_logs, submit_phase_plan]

devops_directive = f"""

--- RECENT CODE CHANGES ---
{diff_output}

CRITICAL DEPLOYMENT DIRECTIVE (ANTI-LOOP ENFORCED):
You are the final gatekeeper. You must follow this exact sequence. Do not deviate.

STEP 1: Call `render_deploy` to trigger the build. If it returns an ERROR, DO NOT call it again.
STEP 2: Call `verify_render_deployment` to monitor the status. Wait for it to finish.
STEP 3: If the status returned is LIVE, approve the deployment:
```json
{{"name": "submit_phase_plan", "arguments": {{"plan_markdown": "### [DEPLOYMENT APPROVED]"}}}}
```
If the status is FAILED, you MUST IMMEDIATELY fetch the logs to find out why. Output exactly this:
```json
{{"name": "get_render_logs", "arguments": {{"service_id": "srv-d798m4chg0os73e3it70"}}}}
```
STEP 4: Read the logs, and submit a phase plan with the exact bug ticket.
"""
state["input"] = state.get("input", "") + devops_directive
print("-> Executing Gate: Heimdall (deployment_infrastructure_skill.md)...")
result = run_single_agent("devops", "Heimdall", "deployment_infrastructure_skill.md", local_config, state, allowed_tools)
print(f"\n>>> [Heimdall OUTPUT]:\n{result}")

if result and "[DEPLOYMENT APPROVED]" in result:
    print("\n>>> [ORCHESTRATOR]: Phase 8 Complete. Live Deployment Successful.")
    # Update state
    state["current_phase"] = "09_uat"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)
    
    sys.exit(0)
else:
    print("\n>>> [ORCHESTRATOR]: 🔴 Deployment Failed or Rejected by Heimdall. Routing back to Phase 1.")
    sprint_history = state.get("sprint_history", [])
    sprint_history.append(f"Deployment Phase Failed: {result.strip()}")
    state["sprint_history"] = sprint_history
    
    history_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(sprint_history)])
    state["input"] = f"SPRINT CONTEXT & NEW BUG REPORT:\n\nSprint History:\n{history_text}\n\nAction Required:\nGenerate a new Bug Ticket based on the latest failure to unblock the sprint."
    state["current_phase"] = "01_intake"
    
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)
    sys.exit(1)
