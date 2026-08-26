import os
import sys
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node
from jarvis_router import get_optimal_compute

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
            return f.read()
    except FileNotFoundError:
        return "ERROR: Artifact missing."

ticket_artifact = read_artifact('02_ticket_artifact.md')

workflow = Workflow('02_Audit')
coulson_node = Node.agent(
    name='Agent Coulson',
    prompt=f'''CRITICAL DIRECTIVE: DO NOT HALLUCINATE OR INVENT FAKE PULL REQUESTS, AGENT NAMES, OR FEATURES. ONLY USE EXACT TEXT FROM THE CONTEXT.

Audit the following Phase 2 Tickets against system constraints and Phase 1 intent:\n\n{ticket_artifact}''',
    system_prompt=load_prompt('agent_coulson_rules.md'),
    llm_config=local_config
)

def audit_router(state):
    out = state.get_node_output('Agent Coulson', '')
    if 'fail' in out.lower() or 'kickback' in out.lower():
        return 'KICKBACK'
    return 'END'

audit_route_node = Node.condition('Audit Router', audit_router)
ids = { 'Agent Coulson': workflow.add_node(coulson_node), 'Audit Router': workflow.add_node(audit_route_node) }
id_to_name = {v: k for k, v in ids.items()}
workflow.connect(ids['Agent Coulson'], ids['Audit Router'])

if __name__ == '__main__':
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get_all_node_outputs()
    
    with open('02_audit_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {k} Audit\n{v}\n\n')
            
    if 'KICKBACK' in str(outputs):
        print("KICKBACK TRIGGERED in Phase 2 Audit")
        sys.exit(3)
        
    print("Phase 02 Audit Complete")
