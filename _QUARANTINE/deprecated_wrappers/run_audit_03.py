import os
import sys
from collections import defaultdict
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node

load_dotenv()
init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f'ERROR: {filename} missing.'

def read_artifact(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
            content = f.read()
            return content.replace('{', '{{').replace('}', '}}')
    except FileNotFoundError:
        return "ERROR: Artifact missing."

def append_to_ledger(entry):
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md', 'a') as f:
        f.write(entry + '\n')
    return 'SUCCESS'

io_tools = [append_to_ledger]

def check_for_kickbacks(outputs):
    for k, v in outputs.items():
        if isinstance(v, str) and ('FAIL' in v.upper() or 'KICKBACK' in v.upper()):
            append_to_ledger('KICKBACK triggered')
            return True
    return False

workflow = Workflow('Audit_03')
coulson = Node.agent(name='Agent Coulson', prompt=f'''CRITICAL DIRECTIVE: DO NOT HALLUCINATE OR INVENT FAKE PULL REQUESTS, AGENT NAMES, OR FEATURES. ONLY USE EXACT TEXT FROM THE CONTEXT.

Audit the following Phase 03 artifacts:

{read_artifact("03_planning_poker_artifact.md")}''', system_prompt=load_prompt('agent_coulson_rules.md'), llm_config=local_config, tools=io_tools)

def coulson_router(state):
    out = state.get_node_output('Agent Coulson', '').lower()
    if 'fail' in out:
        return 'KICKBACK'
    return 'END'

coulson_route = Node.condition('Coulson Router', coulson_router)
ids = { 'Agent Coulson': workflow.add_node(coulson), 'Coulson Router': workflow.add_node(coulson_route) }
id_to_name = {v: k for k, v in ids.items()}
workflow.connect(ids['Agent Coulson'], ids['Coulson Router'])

if __name__ == '__main__':
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get_all_node_outputs()
    with open('03_audit_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {id_to_name.get(k, k)}\n{v}\n\n')
    if 'KICKBACK' in str(outputs) or check_for_kickbacks(outputs):
        sys.exit(3)
    print("Phase 03 Audit Complete")
