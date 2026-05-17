import sys
import os
import json
import re

# Fix import path BEFORE importing gb_config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import sys; sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva"); from gb_config import run_single_agent, local_config

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
    
    directives = (
        "\n\nCRITICAL DIRECTIVES:\n"
        "1. YOU DO NOT HAVE ACCESS TO ANY TOOLS. DO NOT OUTPUT JSON TOOL CALLS.\n"
        "2. DYNAMIC TEST CREATION: Read the GROOMED TICKET carefully. Your test MUST assert the presence of the exact fix required by the current ticket (e.g., asserting that the rogue requirements.txt is deleted). The test must FAIL against the current broken codebase.\n"
        "3. FILE PATHS: When reading project files in your test, always use absolute paths starting with `/home/rdogen/OpenClaw_Factory/projects/Hosteva/`.\n"
        "4. OUTPUT FORMAT: You MUST output the raw Python test code inside a standard ```python ... ``` markdown block. The system will automatically extract this block and save it to `/home/rdogen/OpenClaw_Factory/projects/Hosteva/tests/test_current_bug.py`. Do not include any other markdown code blocks.\n"
        "5. IGNORE SPRINT HISTORY FOR TEST CREATION: The 'ORIGINAL INPUT' contains the full sprint history so you understand context, but you must ONLY write a test for the CURRENT FOCUS TARGET defined in the Groomed Ticket."
    )

    initial_state = {
        "input": f"GROOMED TICKET:\n{groomed_ticket}\n\nORIGINAL INPUT:\n{state.get('input', '')}{directives}"
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
            [] # Empty list to strip tools entirely
        )
        outputs_dict = result_obj if isinstance(result_obj, dict) else {agent_name.replace(" ", "_"): str(result_obj)}
        output_text = outputs_dict.get(agent_name.replace(' ', '_'), str(outputs_dict))
    except Exception as e:
        output_text = f"GraphBit Execution Failed: {str(e)}"
    
    print("\n>>> [PHASE 4 OUTPUT]:")
    print(output_text)
    
    # Extract the python block and write to test file
    test_file_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/tests/test_current_bug.py"
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    
    python_block_match = re.search(r"```python\s*(.*?)\s*```", output_text, re.DOTALL)
    if python_block_match:
        extracted_code = python_block_match.group(1)
        with open(test_file_path, "w") as f:
            f.write(extracted_code)
        print(f"\n-> Extracted Python code and saved directly to {test_file_path}")
    else:
        print("\n-> WARNING: No ```python block found in the output. The test file was not created.")

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
