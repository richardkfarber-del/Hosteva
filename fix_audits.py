import os

common_header = """import os
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

def append_to_ledger(entry):
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md', 'a') as f:
        f.write(entry + '\\n')
    return 'SUCCESS'

io_tools = [append_to_ledger]

def check_for_kickbacks(outputs):
    for k, v in outputs.items():
        if isinstance(v, str) and ('403' in v or 'FAIL' in v.upper() or 'KICKBACK' in v.upper()):
            append_to_ledger(f'KICKBACK triggered by {k}')
            return True
    return False
"""

phases = ['03', '04', '05', '06', '07', '08']
for phase in phases:
    with open(f'/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_audit_{phase}.py', 'w') as f:
        f.write(common_header + f"""
workflow = Workflow('Audit_{phase}')
coulson = Node.agent(name='Agent Coulson', prompt='Audit Phase {phase} artifacts', system_prompt=load_prompt('agent_coulson_rules.md'), llm_config=local_config, tools=io_tools)

def coulson_router(state):
    out = state.get('node_outputs', {{}}).get('Agent Coulson', '').lower()
    if '403' in out or 'fail' in out:
        return 'KICKBACK'
    return 'END'

coulson_route = Node.condition('Coulson Router', coulson_router)
ids = {{ 'Agent Coulson': workflow.add_node(coulson), 'Coulson Router': workflow.add_node(coulson_route) }}
workflow.connect(ids['Agent Coulson'], ids['Coulson Router'])

if __name__ == '__main__':
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get('node_outputs', {{}})
    with open('{phase}_audit_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {{k}}\\n{{v}}\\n\\n')
    if 'KICKBACK' in str(outputs) or check_for_kickbacks(outputs):
        sys.exit(3)
    print("Phase {phase} Audit Complete")
""")
