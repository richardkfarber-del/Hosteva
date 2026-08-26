import os
import re

base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/scrum_pipelines"

tool_mappings = {
    "02_planning.py": "[]",
    "03_backlog.py": "[]",
    "04_tdd.py": "[read_file, write_file, run_shell_command]",
    "05_execution.py": "[read_file, write_file, run_shell_command]",
    "06_review.py": "[read_file, run_shell_command]",
    "07_security.py": "[read_file, run_shell_command]",
    "08_deploy.py": "[run_shell_command]",
    "10_retro.py": "[]",
    "11_memory.py": "[read_file, write_file]",
    "12_executive.py": "[]",
    "13_consolidation.py": "[read_file, write_file, run_shell_command]"
}

for filename, tools in tool_mappings.items():
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename}")
        continue
        
    with open(filepath, "r") as f:
        content = f.read()
        
    if "from swarm_tools import" not in content:
        content = content.replace("from gb_config import", "from swarm_tools import read_file, write_file, run_shell_command\nfrom gb_config import")
        
    if "allowed_tools=" not in content:
        content = re.sub(r'(run_single_agent\([^)]*?,\s*state)\)', r'\1, allowed_tools=' + tools + ')', content)
    
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Updated {filename}")

# Rewrite 09_uat.py
uat_path = os.path.join(base_dir, "09_uat.py")
uat_content = """#!/usr/bin/env python3
import json, os, sys
from swarm_tools import read_file, write_file, run_shell_command
from gb_config import run_single_agent, local_config

print("======================================================")
print("  [PHASE 9] USER ACCEPTANCE TESTING")
print("======================================================")

state_path = os.environ.get("SWARM_STATE_FILE", "../swarm_state.json")
try:
    with open(state_path, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {}

print("-> AGENT-08-QA (Black Widow) bound to qa_generation_skill.md (Frontend UAT)")
print("-> Executing GraphBit Node for Frontend UAT...")
result_ui = run_single_agent("UAT_Frontend", "Black Widow", "qa_generation_skill.md", local_config, state, allowed_tools=[read_file, run_shell_command])
print("\\n>>> [PHASE 9 FRONTEND OUTPUT]:\\n", result_ui)

print("\\n-> AGENT-04-FRONTEND (Spider-Man) bound to core_implementation_skill.md (Backend UAT)")
print("-> Executing GraphBit Node for Backend UAT...")
result_backend = run_single_agent("UAT_Backend", "Spider-Man", "core_implementation_skill.md", local_config, state, allowed_tools=[read_file, run_shell_command])
print("\\n>>> [PHASE 9 BACKEND OUTPUT]:\\n", result_backend)

print(">>> [ORCHESTRATOR]: Phase 9 Complete.")
sys.exit(0)
"""
with open(uat_path, "w") as f:
    f.write(uat_content)
print("Updated 09_uat.py")
