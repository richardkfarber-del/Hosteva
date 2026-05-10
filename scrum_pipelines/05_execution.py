import sys
import os
import json
from gb_config import run_single_agent, local_config

def main():
    print("\n======================================================")
    print("  [PHASE 5] CORE EXECUTION")
    print("======================================================")
    
    state_path = os.environ.get("SWARM_STATE_FILE", os.path.join(os.path.dirname(os.path.dirname(__file__)), "swarm_state.json"))
    try:
        with open(state_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"skills": {}, "kickback_context": None}

    kickback = state.get("kickback_context")
    skill_file = "core_implementation_skill.md"
    
    print("-> AGENT-05 (Iron Man), AGENT-12 (Hulk), AGENT-14 (Wasp), AGENT-16 (Shang-Chi) bound to core_implementation_skill.md")
    print("-> ORCHESTRATION RULE: Enforce SOLID/DRY, mandatory non-silent try/except, semantic commits via GitHub MCP.")
    
    input_context = state.get("input", "")
    if kickback:
        print(f"[!] KICKBACK CONTEXT DETECTED: Injecting downstream error logs into coder context payloads.")
        input_context += f"\n\n[KICKBACK ERROR LOGS]:\n{kickback}"
        
    initial_state = {
        "input": input_context
    }
    
    print("-> Executing GraphBit Node...")
    
    try:
        result_obj = run_single_agent(
            phase_name="Core_Execution",
            agent_name="Core_Execution_Team",
            skill_file=skill_file,
            config=local_config,
            initial_state=initial_state
        )
        outputs_dict = result_obj if isinstance(result_obj, dict) else {agent_name.replace(" ", "_"): str(result_obj)}
        output_text = outputs_dict.get("Core_Execution_Team", str(outputs_dict))
    except Exception as e:
        output_text = f"GraphBit Execution Failed: {str(e)}"
    
    print("\n>>> [PHASE 5 OUTPUT]:")
    print(output_text)
    
    if "### 🔴 [BLOCKING]" in output_text:
        print("\n>>> [ORCHESTRATOR]: Blocking error detected in Execution. Halting pipeline.")
        sys.exit(1)
        
    print("\n>>> [ORCHESTRATOR]: Phase 5 Complete. Implementation executed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
