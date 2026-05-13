#!/usr/bin/env python3
import json, os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config
from swarm_tools import run_shell_command, read_file, write_file, content_search, submit_phase_plan

print("======================================================")
print("  [PHASE 2] SPRINT PLANNING & ARCHITECTURE")
print("======================================================")
print("-> AGENT-02-FRONTEND (Wasp) bound to ui_ux_skill.md")

state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(os.path.dirname(os.path.dirname(__file__)), "swarm_state.json"))
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

allowed_tools = [run_shell_command, read_file, write_file, content_search, submit_phase_plan]

print("-> Executing GraphBit Node...")
result = run_single_agent("wasp", "Wasp", "ui_ux_skill.md", local_config, state, allowed_tools)
print("\n>>> [PHASE 2 OUTPUT]:\n", result)
print(">>> [ORCHESTRATOR]: Phase 2 Complete.")
sys.exit(0)
