#!/usr/bin/env python3
import json, os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config
from swarm_tools import read_file, content_search, submit_phase_plan

print("======================================================")
print("  [PHASE 2] SPRINT PLANNING & ARCHITECTURE")
print("======================================================")
print("-> SCRUM COMMITTEE: Iron Man, Vision, Hulk, Black Panther, Wasp")

state_path = os.environ.get("SWARM_STATE_FILE", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

allowed_tools = [read_file, content_search, submit_phase_plan]

original_input = state.get("input", "")
committee_notes = ""

def get_agent_prompt(notes):
    base = f"{original_input}\n\n"
    if notes:
        base += f"--- PREVIOUS COMMITTEE NOTES ---\n{notes}\n\n"
    base += "DIRECTIVE: Evaluate this ticket strictly from your domain's perspective. If this ticket requires no action or changes from your domain, simply output 'N/A - No impact on my domain'. Do NOT reject the overall ticket, as other domains may still need to work on it."
    return base

def sanitize_output(result):
    if result and "N/A" in result.upper():
        return "N/A - No impact on my domain"
    return result

# ---------------------------------------------------------
# Pass 1: Iron Man (Architecture)
# ---------------------------------------------------------
print("\n-> Executing GraphBit Node: Iron Man (Architecture)...")
state["input"] = get_agent_prompt(committee_notes)
iron_man_result = run_single_agent("architect", "Iron Man", "core_implementation_skill.md", local_config, state, allowed_tools)
print("\n>>> [IRON MAN OUTPUT]:\n", iron_man_result)
committee_notes += f"--- ARCHITECTURE NOTES (Iron Man) ---\n{sanitize_output(iron_man_result)}\n\n"

# ---------------------------------------------------------
# Pass 2: Vision (Data Architect)
# ---------------------------------------------------------
print("\n-> Executing GraphBit Node: Vision (Data Architect)...")
state["input"] = get_agent_prompt(committee_notes)
vision_result = run_single_agent("data_architect", "Vision", "architecture_skill.md", local_config, state, allowed_tools)
print("\n>>> [VISION OUTPUT]:\n", vision_result)
committee_notes += f"--- DATA/SCHEMA NOTES (Vision) ---\n{sanitize_output(vision_result)}\n\n"

# ---------------------------------------------------------
# Pass 3: The Hulk (Backend)
# ---------------------------------------------------------
print("\n-> Executing GraphBit Node: The Hulk (Backend)...")
state["input"] = get_agent_prompt(committee_notes)
hulk_result = run_single_agent("backend", "The Hulk", "backend_engineering_skill.md", local_config, state, allowed_tools)
print("\n>>> [HULK OUTPUT]:\n", hulk_result)
committee_notes += f"--- BACKEND NOTES (The Hulk) ---\n{sanitize_output(hulk_result)}\n\n"

# ---------------------------------------------------------
# Pass 4: Black Panther (Security)
# ---------------------------------------------------------
print("\n-> Executing GraphBit Node: Black Panther (Security)...")
state["input"] = get_agent_prompt(committee_notes)
panther_result = run_single_agent("security", "Black Panther", "security_audit_skill.md", local_config, state, allowed_tools)
print("\n>>> [BLACK PANTHER OUTPUT]:\n", panther_result)
committee_notes += f"--- SECURITY NOTES (Black Panther) ---\n{sanitize_output(panther_result)}\n\n"

# ---------------------------------------------------------
# Pass 5: Wasp (Frontend)
# ---------------------------------------------------------
print("\n-> Executing GraphBit Node: Wasp (Frontend)...")
state["input"] = get_agent_prompt(committee_notes)
wasp_result = run_single_agent("wasp", "Wasp", "ui_ux_skill.md", local_config, state, allowed_tools)
print("\n>>> [WASP OUTPUT]:\n", wasp_result)
committee_notes += f"--- FRONTEND NOTES (Wasp) ---\n{sanitize_output(wasp_result)}\n\n"

# ---------------------------------------------------------
# Artifact Handoff
# ---------------------------------------------------------
final_output = f"{original_input}\n\n{committee_notes}"

artifact_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "02_planning_artifact.md")
with open(artifact_path, "w") as f:
    f.write(final_output if final_output else "No output.")
print(f"-> Saved artifact to {artifact_path}")

# Update state
state["input"] = original_input
state["phase_2_artifact"] = "02_planning_artifact.md"
state["current_phase"] = "03_backlog"
with open(state_path, "w") as f:
    json.dump(state, f, indent=4)
print("-> Updated swarm_state.json")

print(">>> [ORCHESTRATOR]: Phase 2 Complete.")
sys.exit(0)
