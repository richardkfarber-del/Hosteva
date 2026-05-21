import os
import sys
import json
from dotenv import load_dotenv

# Load env before importing gb_config
load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
os.environ["GEMINI_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")

from gb_config import run_single_agent
from graphbit import LlmConfig

BASE_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"
STATE_FILE = os.path.join(BASE_DIR, "swarm_state.json")
REPORT_FILE = os.path.join(BASE_DIR, "MASTER_DIAGNOSTIC_REPORT.md")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"input": "Perform a diagnostic review of the V3 architecture."}

def main():
    print("Igniting Diagnostic Review Pipeline with Gemini 3.1 Pro...")
    state = load_state()
    
    gemini_config = LlmConfig.gemini('gemini-3.1-pro-preview')
    
    mission = """
    MISSION: Review the V3 architecture (scrum_master.py, scrum_pipelines/gb_config.py, scrum_pipelines/swarm_tools.py, scrum_pipelines/05_execution.py, etc).
    Focus on your specific domain. Provide actionable, verifiable recommendations.
    DO NOT HALLUCINATE. Use your tools to read the actual files in /home/rdogen/OpenClaw_Factory/projects/Hosteva.
    Analyze logs like swarm_loop.log and scrum_master.log if needed.
    Identify anti-patterns, missing tools, and how we can improve for Sprint 2.
    """
    state["input"] = mission

    print("\n--- Dispatching Vision (Architecture) ---")
    vision_output = run_single_agent("diagnostic", "Vision", "architecture_skill.md", gemini_config, state)
    
    print("\n--- Dispatching Iron Man (Tooling) ---")
    iron_man_output = run_single_agent("diagnostic", "Iron Man", "core_implementation_skill.md", gemini_config, state)

    print("\n--- Dispatching Shuri (R&D) ---")
    shuri_output = run_single_agent("diagnostic", "Shuri", "qa_generation_skill.md", gemini_config, state)

    print("\n--- Dispatching Rocket (Diagnostics) ---")
    rocket_output = run_single_agent("diagnostic", "Rocket Raccoon", "pr_review_skill.md", gemini_config, state)

    print("\n--- Dispatching Coulson (Process) ---")
    coulson_output = run_single_agent("diagnostic", "Agent Coulson", "scrum_master_skill.md", gemini_config, state)

    print("\nCompiling Master Report...")
    with open(REPORT_FILE, "w") as f:
        f.write("# V3 Architecture Diagnostic Report\n\n")
        f.write("## Vision (Architecture)\n")
        f.write(str(vision_output) + "\n\n")
        f.write("## Iron Man (Tooling)\n")
        f.write(str(iron_man_output) + "\n\n")
        f.write("## Shuri (R&D)\n")
        f.write(str(shuri_output) + "\n\n")
        f.write("## Rocket Raccoon (Diagnostics)\n")
        f.write(str(rocket_output) + "\n\n")
        f.write("## Agent Coulson (Process)\n")
        f.write(str(coulson_output) + "\n\n")

    print(f"\n\u2705 Review Complete. Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()
