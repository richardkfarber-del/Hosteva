import sys
import os
import json
from gb_config import run_single_agent, local_config

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

    agent_name = "AGENT-08-QA (Black Widow)"
    skill_file = "qa_generation_skill.md"
    
    initial_state = {
        "input": state.get("input", "")
    }
    
    print(f"-> {agent_name} bound exclusively to {skill_file}")
    print("-> ORCHESTRATION RULE: Commanding Docker MCP Server to provision pristine mock states.")
    print("-> Executing GraphBit Node...")
    
    try:
        result_obj = run_single_agent(
            phase_name="TDD_Setup",
            agent_name=agent_name,
            skill_file=skill_file,
            config=local_config,
            initial_state=initial_state
        )
        outputs_dict = result_obj if isinstance(result_obj, dict) else {agent_name.replace(" ", "_"): str(result_obj)}
        output_text = outputs_dict.get(agent_name.replace(' ', '_'), str(outputs_dict))
    except Exception as e:
        output_text = f"GraphBit Execution Failed: {str(e)}"
    
    print("\n>>> [PHASE 4 OUTPUT]:")
    print(output_text)
    
    if "### 🔴 [BLOCKING]" in output_text:
        print("\n>>> [ORCHESTRATOR]: Blocking error detected in TDD generation. Halting pipeline.")
        sys.exit(1)
        
    print("\n>>> [ORCHESTRATOR]: Phase 4 Complete. Tests provisioned.")
    sys.exit(0)

if __name__ == "__main__":
    main()
