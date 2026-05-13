import sys
import os
import json

# Fix import path BEFORE importing gb_config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config
from swarm_tools import read_file, write_file, run_shell_command, content_search, submit_phase_plan

def main():
    print("\n======================================================")
    print("  [PHASE 4] TEST-DRIVEN DEVELOPMENT SETUP")
    print("======================================================")
    
    state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(os.path.dirname(os.path.dirname(__file__)), "swarm_state.json"))
    
    try:
        with open(state_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"skills": {}, "kickback_context": None}

    # Load Phase 3 Artifact
    phase_3_artifact_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), state.get("phase_3_artifact", "03_groomed_ticket_artifact.md"))
    try:
        with open(phase_3_artifact_path, "r") as f:
            groomed_ticket = f.read()
    except FileNotFoundError:
        groomed_ticket = "No groomed ticket found."

    agent_name = "AGENT-08-QA (Black Widow)"
    skill_file = "qa_generation_skill.md"
    
    initial_state = {
        "input": f"GROOMED TICKET:\n{groomed_ticket}\n\nORIGINAL INPUT:\n{state.get('input', '')}"
    }
    
    print(f"-> {agent_name} bound exclusively to {skill_file}")
    print("-> ORCHESTRATION RULE: Writing local failing tests to prove the bug exists.")
    print("-> Executing GraphBit Node...")
    
    try:
        # run_single_agent signature: (agent_id, agent_name, skill_file, config, state, allowed_tools)
        result_obj = run_single_agent(
            "QA_Lead",
            agent_name,
            skill_file,
            local_config,
            initial_state,
            [read_file, write_file, run_shell_command, content_search, submit_phase_plan]
        )
        outputs_dict = result_obj if isinstance(result_obj, dict) else {agent_name.replace(" ", "_"): str(result_obj)}
        output_text = outputs_dict.get(agent_name.replace(' ', '_'), str(outputs_dict))
    except Exception as e:
        output_text = f"GraphBit Execution Failed: {str(e)}"
    
    print("\n>>> [PHASE 4 OUTPUT]:")
    print(output_text)
    
    # Save artifact
    artifact_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "04_qa_tests_artifact.md")
    with open(artifact_path, "w") as f:
        f.write(output_text if output_text else "No output.")
    print(f"-> Saved artifact to {artifact_path}")

    # Update state
    state["phase_4_artifact"] = "04_qa_tests_artifact.md"
    state["current_phase"] = "05_execution"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)
    print("-> Updated swarm_state.json")

    if "### \ud83d\udd34 [BLOCKING]" in output_text:
        print("\n>>> [ORCHESTRATOR]: Blocking error detected in TDD generation. Halting pipeline.")
        sys.exit(1)
        
    print("\n>>> [ORCHESTRATOR]: Phase 4 Complete. Tests provisioned.")
    sys.exit(0)

if __name__ == "__main__":
    main()
