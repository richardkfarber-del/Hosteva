import os
import sys

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

# Phase 03: Planning Poker
with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_03_planning_poker.py', 'w') as f:
    f.write(common_header + """
workflow = Workflow('03_Planning_Poker')
hulk = Node.agent(name='Hulk', prompt='Score DB complexity', system_prompt=load_prompt('hulk_rules.md'), llm_config=local_config)
shang_chi = Node.agent(name='Shang-Chi', prompt='Score Logic complexity', system_prompt=load_prompt('shang_chi_rules.md'), llm_config=local_config)
wasp = Node.agent(name='Wasp', prompt='Score UI complexity', system_prompt=load_prompt('wasp_rules.md'), llm_config=local_config)
vision = Node.agent(name='Vision', prompt='Score Arch complexity', system_prompt=load_prompt('vision_rules.md'), llm_config=local_config)
spider_man = Node.agent(name='Spider-Man', prompt='Score QA complexity', system_prompt=load_prompt('spider_man_rules.md'), llm_config=local_config)
ant_man = Node.agent(name='Ant-Man', prompt='Score Docs complexity', system_prompt=load_prompt('ant_man_rules.md'), llm_config=local_config)

nodes = [hulk, shang_chi, wasp, vision, spider_man, ant_man]
ids = {n.name(): workflow.add_node(n) for n in nodes}

workflow.connect(ids['Hulk'], ids['Shang-Chi'])
workflow.connect(ids['Shang-Chi'], ids['Wasp'])
workflow.connect(ids['Wasp'], ids['Vision'])
workflow.connect(ids['Vision'], ids['Spider-Man'])
workflow.connect(ids['Spider-Man'], ids['Ant-Man'])

if __name__ == '__main__':
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get('node_outputs', {})
    with open('03_planning_poker_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {k}\\n{v}\\n\\n')
    if check_for_kickbacks(outputs):
        sys.exit(3)
    print("Phase 03 Complete")
""")

# Phase 08: Retrospective
with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_08_retrospective.py', 'w') as f:
    f.write(common_header + """
workflow = Workflow('08_Retrospective')
winter_soldier = Node.agent(name='Winter Soldier', prompt='Analyze tech debt from sprint artifacts', system_prompt=load_prompt('winter_soldier_rules.md'), llm_config=local_config)
rocket = Node.agent(name='Rocket Raccoon', prompt='Analyze DevOps and VRAM efficiency', system_prompt=load_prompt('rocket_raccoon_rules.md'), llm_config=local_config)

nodes = [winter_soldier, rocket]
ids = {n.name(): workflow.add_node(n) for n in nodes}

workflow.connect(ids['Winter Soldier'], ids['Rocket Raccoon'])

if __name__ == '__main__':
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    outputs = final_state.get('node_outputs', {})
    with open('08_retrospective_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {k}\\n{v}\\n\\n')
    if check_for_kickbacks(outputs):
        sys.exit(3)
    print("Phase 08 Complete")
""")

# Special Ops
with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_special_ops.py', 'w') as f:
    f.write(common_header + """
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
    outputs = final_state.get('node_outputs', {})
    with open('special_ops_artifact.md', 'w') as f:
        for k, v in outputs.items():
            f.write(f'# {k}\\n{v}\\n\\n')
    print("Special Ops Complete")
""")

# Audits
for phase in ['03', '08']:
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

# Rename existing files to shift numbers
renames = [
    ('run_06_shadow_ops.py', 'run_07_shadow_ops.py'),
    ('run_05_qa_deploy.py', 'run_06_qa_deploy.py'),
    ('run_04_development.py', 'run_05_development.py'),
    ('run_03_environment_setup.py', 'run_04_environment_setup.py'),
    ('run_audit_05.py', 'run_audit_06.py'),
    ('run_audit_04.py', 'run_audit_05.py'),
    ('run_audit_03.py', 'run_audit_04.py')
]

for old, new in renames:
    old_path = os.path.join('/home/rdogen/OpenClaw_Factory/projects/Hosteva', old)
    new_path = os.path.join('/home/rdogen/OpenClaw_Factory/projects/Hosteva', new)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        with open(new_path, 'r') as f:
            content = f.read()
        if '03_' in old: content = content.replace('03_', '04_').replace('Phase 03', 'Phase 04')
        elif '04_' in old: content = content.replace('04_', '05_').replace('Phase 04', 'Phase 05')
        elif '05_' in old: content = content.replace('05_', '06_').replace('Phase 05', 'Phase 06')
        elif '06_' in old: content = content.replace('06_', '07_').replace('Phase 06', 'Phase 07')
        with open(new_path, 'w') as f:
            f.write(content)
