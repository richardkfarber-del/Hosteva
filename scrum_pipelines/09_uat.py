#!/usr/bin/env python3
import json, os, sys, subprocess
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(project_root, ".env"))

sys.path.append(project_root)
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config
from swarm_tools import submit_phase_plan, run_shell_command

print("======================================================")
print("  [PHASE 9] USER ACCEPTANCE TESTING (UAT)")
print("======================================================")

state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(project_root, "swarm_state.json"))
os.chdir(project_root)

try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

allowed_tools = [run_shell_command, submit_phase_plan]

uat_directive = """
CRITICAL UAT DIRECTIVE:
You are Spider-Man, the UI/UX expert. The deployment was pushed, but the user reported that the logo is STILL missing on the live site.

Your job is to figure out WHY. The Jinja2 code was fixed, but does the actual image file exist?

Use your `run_shell_command` tool to check if the `hosteva_logo.png` file actually exists in the `ARCHIVE_DOCS/Hosteva_Hidden/static/img/` directory (or wherever the static folder is located).

If the file is missing, you MUST fail the UAT by outputting exactly:
```json
{"name": "submit_phase_plan", "arguments": {"plan_markdown": "### 🔴 [UAT FAILED]: The logo image file is physically missing from the repository."}}
```
"""

state["input"] = state.get("input", "") + uat_directive

print("-> Executing Gate: Spider-Man (ui_ux_skill.md)...")
result = run_single_agent("frontend", "Spider-Man", "ui_ux_skill.md", local_config, state, allowed_tools)
print(f"\n>>> [Spider-Man OUTPUT]:\n{result}")

if result and "### 🔴 [UAT FAILED]" in result:
    print("\n>>> [ORCHESTRATOR]: 🔴 UAT Failed. Asset missing. Halting pipeline.")
    sys.exit(1)
else:
    print("\n>>> [ORCHESTRATOR]: Phase 9 Complete. UAT Passed.")
    sys.exit(0)
