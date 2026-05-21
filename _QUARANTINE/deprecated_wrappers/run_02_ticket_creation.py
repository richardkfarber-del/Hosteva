import os
import sys
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node
from jarvis_router import get_optimal_compute
import re

load_dotenv()
init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')


def load_system_prompt(agent_name, rules_file):
    rules = load_prompt(rules_file)
    memory_file = f"agent_memories/{agent_name.lower().replace(' ', '-')}.md"
    try:
        with open(os.path.join(os.path.dirname(__file__), memory_file), 'r') as f:
            memory = f.read()
    except FileNotFoundError:
        memory = ""
    return f"{rules}\n\n=== PAST MEMORY & EXPERTISE ===\n{memory}\n\n=== CRITICAL DIRECTIVE ===\n\nThe above is your PAST memory. You must retain the technical expertise, but DO NOT rebuild past features.\n\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below.\n\nSCOPE ADHERENCE DIRECTIVE: You must strictly adhere to the scope of the provided Sprint Backlog. Do not invent or recommend out-of-scope tasks (such as market research, SEO, or user surveys) UNLESS they are explicitly requested in the Backlog.\n"

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f'ERROR: {filename} missing.'

def read_artifact(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "ERROR: Artifact missing."

try:
    with open(os.path.join(os.path.dirname(__file__), '00_context_backend.md'), 'r') as f:
        memory_context = f.read()
except FileNotFoundError:
    memory_context = "ERROR: Memory context missing."

phase1_artifact = read_artifact('phase1_artifact.md')
spike_artifact = read_artifact('SPIKE_FEAT-013.md')

# Strip out the Falcon research noise to prevent anchoring
phase1_artifact = re.sub(r'(?i)##.*?Falcon.*?\n(.*?)(?=##|$)', '', phase1_artifact, flags=re.DOTALL)
phase1_artifact = re.sub(r'Based on the provided Architecture Decision Record.*?Timeline:.*?research conducted\.', '', phase1_artifact, flags=re.DOTALL)

# Priority 4: Scaffolding & Sandboxing - Prompt modification
full_hawkeye_prompt = f'''PROJECT MEMORY:
{memory_context}

Convert the following Phase 1 Planning Artifact and Spike Research into detailed engineering tickets. 

CRITICAL CONTEXT: The Research phase is already COMPLETE as detailed in the Spike Artifact. DO NOT generate any tickets for research, scouting, or investigation. You must generate strictly engineering execution tickets (Backend, Frontend, Database, Legal/Compliance) to implement the architecture described in the ADR and Spike.

IMPORTANT NOTE FOR LEGAL TICKETS:
We do not yet have terms of service or a privacy policy. The updates required by the Spike will be the FIRST entries in our terms of service and privacy policy. Ensure the legal ticket explicitly states that we are creating the terms of service and privacy policy now, and as the project progresses and we add to them, we will clean up the documents themselves. But for now, these will be the first entries we have documented.

YOU MUST USE THIS EXACT FORMAT FOR EVERY TICKET:

**Ticket X:** [Agent Name] - [Task Description]
**Files to Modify:**
- `/path/to/file1.py`
- `/path/to/file2.js`

**CRITICAL:** For each ticket, you MUST include a "Files to Modify" section. Analyze the project memory and the plan to identify the exact, absolute file paths that the developer will need to edit. If a file does not exist, specify that it needs to be created. This is a mandatory step to prevent developers from guessing file paths.

Failure to use the "**Ticket X:**" and "**Files to Modify:**" format will crash the pipeline.

=== PHASE 1 PLANNING ARTIFACT ===
{phase1_artifact}

=== SPIKE RESEARCH ARTIFACT ===
{spike_artifact}'''

safe_sys = load_system_prompt('Hawkeye', 'hawkeye_rules.md').replace('{', '{{').replace('}', '}}')
safe_prompt = full_hawkeye_prompt.replace('{', '{{').replace('}', '}}')

# Changed workflow name to force a fresh execution
workflow = Workflow('02_Ticket_Creation_V5')
local_config = LlmConfig.ollama('llama3.1-orchestrator')
hawkeye_node = Node.agent(
    name='Hawkeye',
    prompt=safe_prompt,
    system_prompt=safe_sys,
    llm_config=local_config
)

def hawkeye_router(state):
    out = state.get_node_output('Hawkeye', '')
    if 'missing info' in out.lower() or 'kickback' in out.lower():
        return 'KICKBACK'
    return 'END'

hawkeye_route_node = Node.condition('Hawkeye Router', hawkeye_router)
ids = { 'Hawkeye': workflow.add_node(hawkeye_node), 'Hawkeye Router': workflow.add_node(hawkeye_route_node) }
id_to_name = {v: k for k, v in ids.items()}
workflow.connect(ids['Hawkeye'], ids['Hawkeye Router'])

if __name__ == '__main__':
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get_all_node_outputs()
    
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/02_ticket_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {id_to_name.get(k, k)}\n{v}\n\n')
            
    if 'KICKBACK' in str(outputs):
        print("KICKBACK TRIGGERED in Phase 2")
        sys.exit(3)
        
    print("Phase 02 Complete")
