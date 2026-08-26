import os
import subprocess
import json
import time

# PROJECT PHOENIX: Native Agentic Loop
# This loop acts as the central heartbeat of the Swarm. It does not parse LLM output.
# It simply passes the current state and tools to the LLM, allowing the LLM to drive the execution.

SPRINT_GOAL_FILE = "SPIKE_FEAT-013.md"
BACKLOG_FILE = "SPRINT_BACKLOG.md"

def get_system_prompt():
    return """
    You are the Hosteva Swarm, operating under Project Phoenix directives.
    You are a completely autonomous, tool-driven Scrum team.
    
    Your Objective: Execute Sprint 13 (FEAT-013) to completion.
    
    RULES OF ENGAGEMENT:
    1. You have native access to the terminal (shell) and filesystem (file_read, file_write).
    2. DO NOT wait for Python wrappers to tell you what to do. You drive the workflow.
    3. Read the SPIKE_FEAT-013.md file to understand the goal.
    4. Plan the sprint, write the tickets to SPRINT_BACKLOG.md.
    5. Execute the code, write it to the workspace.
    6. Run your own tests using the `shell` tool (e.g., `pytest`).
    7. IF A TEST FAILS: Read the error and fix the code immediately. Do not halt.
    8. When all tests pass and the feature is deployed, write "SPRINT 13 COMPLETE" to the terminal.
    """

def execute_loop():
    print("🔥 IGNITING PROJECT PHOENIX NATIVE LOOP 🔥")
    print(f"Targeting Sprint Goal: {SPRINT_GOAL_FILE}")
    
    # In a fully realized ZeroClaw environment, this is where we invoke the core agent
    # with agentic=True and allowed_tools=["shell", "file_read", "file_write"].
    # Since this script acts as the entry point, we will simulate handing control over
    # to the ZeroClaw agentic runtime.
    
    print("\n[SYSTEM] Handing execution control to Native Agentic Runtime...")
    print("[SYSTEM] Awaiting autonomous tool execution from the Swarm.\n")

if __name__ == "__main__":
    execute_loop()
