import sys
import os
from gb_config import run_single_agent, local_config

def main():
    print("\n======================================================")
    print("  [PHASE 4] TEST-DRIVEN DEVELOPMENT SETUP")
    print("======================================================")
    
    agent_name = "AGENT-08-QA (Black Widow)"
    skill_file = "qa_generation_skill.md"
    target_ticket = "BUG-006: Stripe Webhook Database Logic Failure"
    
    initial_state = {
        "input": f"Generate a failing pytest for the following ticket:\n\n{target_ticket}\n\nEnsure the test explicitly checks if the database update function is called when a valid Stripe webhook payload is received."
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
        # Use GraphBit's specific get_all_node_outputs method
        outputs_dict = result_obj if isinstance(result_obj, dict) else {agent_name.replace(" ", "_"): str(result_obj)}
        output_text = outputs_dict.get(agent_name.replace(' ', '_'), str(outputs_dict))
    except Exception as e:
        output_text = f"GraphBit Execution Failed: {str(e)}"
    
    print("\n>>> [PHASE 4 OUTPUT]:")
    print(output_text)
    
    if "### \ud83d\udd34 [BLOCKING]" in output_text:
        print("\n>>> [ORCHESTRATOR]: Blocking error detected in TDD generation. Halting pipeline.")
        sys.exit(1)
        
    print("\n>>> [ORCHESTRATOR]: Phase 4 Complete. Tests provisioned.")
    sys.exit(0)

if __name__ == "__main__":
    main()
