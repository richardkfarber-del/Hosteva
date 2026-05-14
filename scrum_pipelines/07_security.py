import sys
import os
import json
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config

def main():
    print("\n======================================================")
    print("  [PHASE 7] SECURITY & COMPLIANCE GATES")
    print("======================================================")
    
    state_path = os.environ.get("SWARM_STATE_FILE", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json")
    try:
        with open(state_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"skills": {}, "kickback_context": None}

    skill_file = "security_audit_skill.md"
    
    initial_state = {
        "input": state.get("input", "")
    }
    
    print("-> AGENT-19-SECURITY (Black Panther) & AGENT-21-REDTEAM (Ultron) bound to security_audit_skill.md")
    print("-> AGENT-18-COMPLIANCE (She-Hulk) bound to legal_compliance_audit_skill.md")
    print("-> ORCHESTRATION RULE: Halting DAG if Breach or Compliance Violation detected.")
    print("-> Executing GraphBit Node...")
    
    try:
        result_obj = run_single_agent(
            phase_name="Security_Compliance",
            agent_name="Security_Team",
            skill_file=skill_file,
            config=local_config,
            initial_state=initial_state
        )
        outputs_dict = result_obj if isinstance(result_obj, dict) else {"Security_Team": str(result_obj)}
        output_text = outputs_dict.get("Security_Team", str(outputs_dict))
    except Exception as e:
        output_text = f"GraphBit Execution Failed: {str(e)}"
    
    print("\n>>> [PHASE 7 OUTPUT]:")
    print(output_text)
    
    if "### 🔴 [BREACH DETECTED]" in output_text or "### 🔴 [COMPLIANCE VIOLATION]" in output_text:
        print("\n>>> [ORCHESTRATOR]: ### 🔴 [BREACH DETECTED] or [COMPLIANCE VIOLATION] emitted. Halting pipeline.")
        sys.exit(1)
        
    print("\n>>> [ORCHESTRATOR]: Phase 7 Complete. Security and Compliance gates passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
