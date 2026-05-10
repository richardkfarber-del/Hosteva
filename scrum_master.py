import os
import sys
import json
import subprocess

BASE_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"
PIPELINES_DIR = os.path.join(BASE_DIR, "scrum_pipelines")
STATE_FILE = os.path.join(BASE_DIR, "swarm_state.json")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

def load_skill(skill_name):
    path = os.path.join(SKILLS_DIR, skill_name)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return ""

def init_state():
    state = {
        "status": "in_progress",
        "current_phase": "01_intake",
        "kickback_context": "",
        "skills": {
            "architecture": load_skill("architecture_skill.md"),
            "pr_review": load_skill("pr_review_skill.md"),
            "qa_generation": load_skill("qa_generation_skill.md")
        },
        "strikes": 0
    }
    save_state(state)
    return state

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return init_state()

def run_phase(script_name):
    print(f"\n=== Starting Phase: {script_name} ===")
    env = os.environ.copy()
    env["SWARM_STATE_FILE"] = STATE_FILE
    
    script_path = os.path.join(PIPELINES_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"[WARNING] {script_name} not found. Skipping.")
        return 0

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True, text=True, env=env
    )
    print(result.stdout)
    if result.stderr:
        print(f"ERROR in {script_name}: {result.stderr}")
    return result.returncode

def main():
    print("Igniting V3 Master Orchestrator...")
    state = init_state()
    
    # Phase 1-4: Planning & TDD
    for phase in ["01_intake.py", "02_planning.py", "03_backlog.py", "04_tdd.py"]:
        if run_phase(phase) != 0:
            print(f"Critical failure in planning phase: {phase}. Halting.")
            sys.exit(1)

    # Phase 5-7: Execution, Review, QA (The Core Kickback Loop)
    max_strikes = 3
    success = False

    while state["strikes"] < max_strikes:
        print(f"\n--- Sprint Iteration {state['strikes'] + 1} ---")
        
        # Phase 5: Execution
        code_exec = run_phase("05_execution.py")
        if code_exec != 0:
            state["strikes"] += 1
            state["kickback_context"] = "Execution failed. Review logs."
            save_state(state)
            continue

        # Phase 6: PR Review
        code_review = run_phase("06_review.py")
        if code_review != 0:
            state["strikes"] += 1
            state["kickback_context"] = "PR Review rejected. Fix code."
            save_state(state)
            print("Kickback triggered by PR Review. Routing back to Phase 5.")
            continue

        # Phase 7: Security Audit
        code_sec = run_phase("07_security.py")
        if code_sec != 0:
            state["strikes"] += 1
            state["kickback_context"] = "Security audit failed. Fix vulnerabilities."
            save_state(state)
            print("Kickback triggered by Security. Routing back to Phase 5.")
            continue

        # If we reach here, the core loop passed
        success = True
        break

    if not success:
        print("\n🚨 MAX STRIKES REACHED. TRIGGERING ROCKET RACCOON FAILSAFE 🚨")
        run_phase("rocket_failsafe.py")
        print("Pipeline Halted.")
        sys.exit(1)

    # Phase 8-13: Deploy to Consolidation
    for phase in ["08_deploy.py", "09_uat.py", "10_retro.py", "11_memory.py", "12_executive.py", "13_consolidation.py"]:
        run_phase(phase)

    print("\n✅ FULL SPRINT PIPELINE COMPLETE")

if __name__ == "__main__":
    main()
