import os
import sys
from collections import defaultdict
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node
from jarvis_router import get_optimal_compute

load_dotenv()
init()

local_config = LlmConfig.ollama('llama3.1-orchestrator')


def load_system_prompt(agent_name, rules_file):
    rules = load_prompt(rules_file)
    return f"{rules}\n\n=== CRITICAL DIRECTIVE ===\n\nYour CURRENT task is defined EXCLUSIVELY by the active Sprint Backlog and the artifacts provided below. DO NOT reference past test failures or external logs.\n"

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f'ERROR: {filename} missing.'

def check_for_kickbacks(outputs):
    for k, v in outputs.items():
        if isinstance(v, str) and ('__KICKBACK__' in v.upper() or '__FAIL__' in v.upper()):
            return True
    return False

try:
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/02_ticket_artifact.md', 'r') as f:
        tickets = f.read()
except FileNotFoundError:
    tickets = "ERROR: Tickets missing."

poker_prompt = f"Review the following tickets and score the complexity for your domain:\n\n{tickets}"

workflow = Workflow('03_Planning_Poker')
hulk = Node.agent(name='Hulk', prompt=poker_prompt, system_prompt=load_system_prompt('Hulk', 'hulk_rules.md'), llm_config=get_optimal_compute('Hulk', 'planning'))
shang_chi = Node.agent(name='Shang-Chi', prompt=poker_prompt, system_prompt=load_system_prompt('Shang-Chi', 'shang_chi_rules.md'), llm_config=get_optimal_compute('Shang-Chi', 'planning'))
wasp = Node.agent(name='Wasp', prompt=poker_prompt, system_prompt=load_system_prompt('Wasp', 'wasp_rules.md'), llm_config=get_optimal_compute('Wasp', 'planning'))
vision = Node.agent(name='Vision', prompt=poker_prompt, system_prompt=load_system_prompt('Vision', 'vision_rules.md'), llm_config=get_optimal_compute('Vision', 'planning'))
spider_man = Node.agent(name='Spider-Man', prompt=poker_prompt, system_prompt=load_system_prompt('Spider-Man', 'spider_man_rules.md'), llm_config=get_optimal_compute('Spider-Man', 'planning'))
ant_man = Node.agent(name='Ant-Man', prompt=poker_prompt, system_prompt=load_system_prompt('Ant-Man', 'ant_man_rules.md'), llm_config=get_optimal_compute('Ant-Man', 'planning'))

nodes = [hulk, shang_chi, wasp, vision, spider_man, ant_man]
ids = {n.name(): workflow.add_node(n) for n in nodes}
id_to_name = {v: k for k, v in ids.items()}

workflow.connect(ids['Hulk'], ids['Shang-Chi'])
workflow.connect(ids['Shang-Chi'], ids['Wasp'])
workflow.connect(ids['Wasp'], ids['Vision'])
workflow.connect(ids['Vision'], ids['Spider-Man'])
workflow.connect(ids['Spider-Man'], ids['Ant-Man'])

if __name__ == '__main__':
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get_all_node_outputs()
    with open('03_planning_poker_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {id_to_name.get(k, k)}\n{v}\n\n')
    if check_for_kickbacks(outputs):
        sys.exit(3)
    print("Phase 03 Complete")
