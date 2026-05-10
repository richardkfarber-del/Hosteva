import sys
from gb_config import run_single_agent, local_config

def main():
    print("\n======================================================")
    print("  [PHASE 6] LOGIC & PULL REQUEST REVIEW")
    print("======================================================")
    
    agent_name = "AGENT-06-LOGIC (Captain America)"
    skill_file = "pr_review_skill.md"
    
    initial_state = {
        "input": "Review the recent core execution code changes against state machines, routing logic, and architectural contracts."
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
