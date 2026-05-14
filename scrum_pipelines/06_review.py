import sys
import os
import json
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config

def main():
    print("\n======================================================")
    print("  [PHASE 6] LOGIC & PULL REQUEST REVIEW")
    print("======================================================")
    
    state_path = os.environ.get("SWARM_STATE_FILE", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json")
    try:
        with open(state_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"skills": {}, "kickback_context": None}

    agent_name = "AGENT-06-LOGIC (Captain America)"
    skill_file = "pr_review_skill.md"
    
    initial_state = {
        "input": state.get("input", "")
    }
    
    print(f"-> {agent_name} bound exclusively to {skill_file}")
    print("-> ORCHESTRATION RULE: Enforcing strict Logic/PR Review. Circuit breaker active.")
    print("-> Executing GraphBit Node...")
    
    try:
        result_obj = run_single_agent(
            phase_name="PR_Review",
            agent_name=agent_name.replace(' ', '_'),
            skill_file=skill_file,
            config=local_config,
            initial_state=initial_state
        )
        outputs_dict = result_obj if isinstance(result_obj, dict) else {agent_name.replace(" ", "_"): str(result_obj)}
        output_text = outputs_dict.get(agent_name.replace(' ', '_'), str(outputs_dict))
    except Exception as e:
        output_text = f"GraphBit Execution Failed: {str(e)}"
    
    print("\n>>> [PHASE 6 OUTPUT]:")
    print(output_text)
    
    if "### 🔴 [BLOCKING]" in output_text:
        print("\n>>> [ORCHESTRATOR]: ### 🔴 [BLOCKING] state emitted by Captain America. Initiating Kickback Loop.")
        sys.exit(1)
        
    print("\n>>> [ORCHESTRATOR]: Phase 6 Complete. PR Review passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
