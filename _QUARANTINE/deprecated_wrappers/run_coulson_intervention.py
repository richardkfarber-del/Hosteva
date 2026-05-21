import os
import sys
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node
from jarvis_router import get_optimal_compute
import subprocess

load_dotenv()
init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f'ERROR: {filename} missing.'

def count_consecutive_kickbacks():
    strike_file = os.path.join(os.path.dirname(__file__), 'swarm_state.json')
    import json
    count = 0
    if os.path.exists(strike_file):
        with open(strike_file, 'r') as f:
            try:
                data = json.load(f)
                count = data.get('kickback_count', 0)
            except:
                pass
    count += 1
    with open(strike_file, 'w') as f:
        json.dump({'kickback_count': count}, f)
    return count

def get_latest_context():
    context = ""
    
    # Read ledger
    ledger_path = os.path.join(os.path.dirname(__file__), 'daily_ledger.md')
    if os.path.exists(ledger_path):
        with open(ledger_path, 'r') as f:
            context += "\n--- DAILY LEDGER ---\n" + f.read()
            
    # Read latest artifacts (just 3 and 4 for now based on where it stalled)
    for artifact in ['03_planning_poker_artifact.md', '03_audit_artifact.md', '04_environment_artifact.md', '04_audit_artifact.md']:
        path = os.path.join(os.path.dirname(__file__), artifact)
        if os.path.exists(path):
            with open(path, 'r') as f:
                context += f"\n--- {artifact} ---\n" + f.read()[:5000] # Limit size to prevent context window blowout
                
    return context.replace('{', '{{').replace('}', '}}')

workflow = Workflow('Coulson_Intervention')

context_data = get_latest_context()

agent_coulson_node = Node.agent(
    name='Agent Coulson',
    prompt=f'A kickback occurred in the assembly line. Review the following recent artifacts and daily_ledger.md to determine where the failure occurred. CRITICAL DIRECTIVE: DO NOT HALLUCINATE OR INVENT FAKE PULL REQUESTS, AGENT NAMES, OR FEATURES. ONLY CITE EXACT TEXT FROM THE CONTEXT PROVIDED. Output a routing decision or an ALARM for Nick Fury.\n\nCONTEXT:\n{context_data}',
    system_prompt=load_prompt('agent_coulson_rules.md'),
    llm_config=local_config
)

ids = {'Agent Coulson': workflow.add_node(agent_coulson_node)}
id_to_name = {v: k for k, v in ids.items()}

if __name__ == '__main__':
    kickback_count = count_consecutive_kickbacks()
    print(f"Coulson detected {kickback_count} consecutive kickbacks.")
    
    if kickback_count >= 3:
        print("🚨 3-Strike Limit Hit. Escalating to Rocket Raccoon.")
        # Dispatch Rocket
        rocket_path = os.path.join(os.path.dirname(__file__), 'dispatch_rocket.py')
        if os.path.exists(rocket_path):
             subprocess.run([sys.executable, rocket_path])
        else:
             print("ERROR: dispatch_rocket.py not found.")
        # Halt pipeline
        sys.exit(1)

    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get_all_node_outputs()
    
    coulson_output = outputs.get('Agent Coulson', '')
    
    log_path = os.path.join(os.path.dirname(__file__), 'coulson_intervention_log.md')
    with open(log_path, 'w') as f:
        f.write(f'# Coulson Intervention\n\n{coulson_output}')
        
    print(f"Coulson Intervention Complete. Output:\n{coulson_output}")
    sys.exit(0)
