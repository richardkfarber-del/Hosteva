#!/usr/bin/env python3
import json, os, sys
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(project_root, ".env"))

sys.path.append(project_root)
from gb_config import run_single_agent, local_config
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
You are Black Widow, the Lead QA Engineer. You must perform a full User Acceptance Test on the live production site using a real headless browser.

STEP 1: Use your `run_shell_command` tool to execute the full UAT browser suite: 
`python3 tests/uat_full_suite.py`

STEP 2: Read the output of the test script. 
- If the script outputs "UAT SUCCESS", call `submit_phase_plan` with exactly: "### 🟢 [UAT PASSED]"
- If the script outputs "UAT FAILED" (e.g., a 502 Bad Gateway or browser crash), call `submit_phase_plan` with exactly: "### 🔴 [UAT FAILED]: The site crashed during browser testing. <include the error>"
"""

state["input"] = state.get("input", "") + "\n\n" + uat_directive

print("-> Executing Gate: Black Widow (uat_skill.md)...")
result = run_single_agent("black-widow", "Black Widow", "uat_skill.md", local_config, state, allowed_tools)
print(f"\n>>> [Black Widow OUTPUT]:\n{result}")

if result and "[UAT FAILED]" in result:
    print("\n>>> [ORCHESTRATOR]: 🔴 UAT Failed. Live site crashed. Routing back to Phase 1.")
    sprint_history = state.get("sprint_history", [])
    sprint_history.append(f"UAT Phase Failed: {result.strip()}")
    state["sprint_history"] = sprint_history
    
    history_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(sprint_history)])
    state["input"] = f"SPRINT CONTEXT & NEW BUG REPORT:\n\nSprint History:\n{history_text}\n\nAction Required:\nGenerate a new Bug Ticket based on the latest failure to unblock the sprint."
    state["current_phase"] = "01_intake"
    
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)
    sys.exit(1)
else:
    print("\n>>> [ORCHESTRATOR]: Phase 9 Complete. UAT Passed.")
    sys.exit(0)
