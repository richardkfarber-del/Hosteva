import os
import sys
from collections import defaultdict
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

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ad-Hoc Special Ops Launcher')
    parser.add_argument('--team', nargs='+', required=True, help='List of agents to deploy')
    parser.add_argument('--mission', type=str, required=True, help='Mission prompt')
    args = parser.parse_args()

    workflow = Workflow('Special_Ops')
    prev_id = None
    
    for agent_name in args.team:
        node = Node.agent(agent_name, args.mission, load_prompt(f'{agent_name.lower().replace(" ", "_")}_rules.md'), local_config)
        curr_id = workflow.add_node(node)
        if prev_id is not None:
            workflow.connect(prev_id, curr_id)
        prev_id = curr_id

    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get_all_node_outputs()
    with open('special_ops_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {k}\n{v}\n\n')
    print("Special Ops Complete")
