import os
from swarm_tools import run_shell_command, read_file, write_file
from collections import defaultdict
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node

load_dotenv()
init()

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f'ERROR: {filename} missing.'

local_config = LlmConfig.ollama("llama3.1-orchestrator")
coder_config = LlmConfig.ollama('qwen2.5-coder:7b')

def append_to_ledger(entry):
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md', 'a') as f:
        f.write(entry + '\n')
    return 'SUCCESS'

io_tools = [append_to_ledger, run_shell_command, read_file, write_file]

backlog_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPRINT_BACKLOG.md'
try:
    with open(backlog_path, 'r') as f:
        backlog_content = f.read()
except FileNotFoundError:
    backlog_content = "ERROR: SPRINT_BACKLOG.md not found."

nick_fury_node = Node.agent(name='Nick Fury', prompt=f'Intake the following backlog:\n\n{backlog_content}', system_prompt=load_prompt('nick_fury_rules.md'), llm_config=local_config)
vision_node = Node.agent(name='Vision', prompt='ADR', system_prompt=load_prompt('vision_rules.md'), llm_config=local_config)
falcon_node = Node.agent(name='Falcon', prompt='Research', system_prompt=load_prompt('falcon_rules.md'), llm_config=local_config)
iron_man_arch_node = Node.agent(name='Iron Man Arch', prompt='Arch', system_prompt=load_prompt('iron_man_rules.md'), llm_config=coder_config)
she_hulk_node = Node.agent(name='She-Hulk', prompt='Legal', system_prompt=load_prompt('she_hulk_rules.md'), llm_config=local_config)
black_panther_node = Node.agent(name='Black Panther', prompt='Security', system_prompt=load_prompt('black_panther_rules.md'), llm_config=local_config)
wasp_ui_node = Node.agent(name='Wasp UI', prompt='UI/UX', system_prompt=load_prompt('wasp_rules.md'), llm_config=coder_config)
hawkeye_node = Node.agent(name='Hawkeye', prompt=f'Generate tickets for the following backlog:\n\n{backlog_content}\n\nNote: This is a single bug fix. Do not trigger THE_SINGLE_FEATURE_RULE.', system_prompt=load_prompt('hawkeye_rules.md'), llm_config=local_config)
hulk_node = Node.agent(name='Hulk', prompt='DB Load', system_prompt=load_prompt('hulk_rules.md'), llm_config=local_config)
shang_chi_node = Node.agent(name='Shang-Chi', prompt='Logic Load', system_prompt=load_prompt('shang_chi_rules.md'), llm_config=local_config)
spider_man_plan_node = Node.agent(name='Spider-Man Plan', prompt='Env Load', system_prompt=load_prompt('spider_man_rules.md'), llm_config=local_config)
ant_man_node = Node.agent(name='Ant-Man', prompt='Docs Load', system_prompt=load_prompt('ant_man_rules.md'), llm_config=local_config)
jarvis_vram_node = Node.agent(name='Jarvis VRAM', prompt='VRAM Load', system_prompt=load_prompt('jarvis_rules.md'), llm_config=local_config)
captain_america_node = Node.agent(name='Captain America', prompt='VRAM Gate', system_prompt=load_prompt('captain_america_rules.md'), llm_config=local_config)
black_widow_node = Node.agent(name="Black Widow", prompt="TDD", system_prompt=load_prompt("black_widow_rules.md"), llm_config=local_config, tools=io_tools)
iron_man_node = Node.agent(name="Iron Man", prompt="Backend", system_prompt=load_prompt("iron_man_rules.md"), llm_config=coder_config, tools=io_tools)
wasp_node = Node.agent(name="Wasp", prompt="Frontend", system_prompt=load_prompt("wasp_rules.md"), llm_config=coder_config, tools=io_tools)
agent_coulson_node = Node.agent(name='Agent Coulson', prompt='Audit', system_prompt=load_prompt('agent_coulson_rules.md'), llm_config=local_config, tools=io_tools)
jarvis_diag_node = Node.agent(name='Jarvis Diag', prompt='Diag', system_prompt=load_prompt('jarvis_rules.md'), llm_config=local_config)
quicksilver_node = Node.agent(name="Quicksilver", prompt="PR", system_prompt=load_prompt("quicksilver_rules.md"), llm_config=local_config, tools=io_tools)
spider_man_env_node = Node.agent(name='Spider-Man Env', prompt='QA Env', system_prompt=load_prompt('spider_man_rules.md'), llm_config=local_config)
heimdall_node = Node.agent(name="Heimdall", prompt="Deploy", system_prompt=load_prompt("heimdall_rules.md"), llm_config=local_config, tools=io_tools)
ultron_node = Node.agent(name='Ultron', prompt='Pen-test', system_prompt=load_prompt('ultron_rules.md'), llm_config=local_config)
thanos_node = Node.agent(name='Thanos', prompt='Chaos', system_prompt=load_prompt('thanos_rules.md'), llm_config=local_config)
star_lord_node = Node.agent(name='Star-Lord', prompt='Marketing', system_prompt=load_prompt('star_lord_rules.md'), llm_config=local_config)
wanda_node = Node.agent(name='Wanda', prompt='Maxims', system_prompt=load_prompt('wanda_maximoff_rules.md'), llm_config=local_config)
kang_node = Node.agent(name='Kang', prompt='Tools', system_prompt=load_prompt('kang_rules.md'), llm_config=local_config)
shuri_node = Node.agent(name='Shuri', prompt='Updates', system_prompt=load_prompt('shuri_rules.md'), llm_config=local_config)
rocket_raccoon_node = Node.agent(name='Rocket Raccoon', prompt='Failsafe', system_prompt=load_prompt('rocket_rules.md'), llm_config=local_config, tools=io_tools)
end_node = Node.agent(name='END', prompt='Workflow Complete.', system_prompt='Workflow Complete.', llm_config=local_config)

def hawkeye_router(state):
    out = state.node_outputs.get('Hawkeye', '')
    if '403' in out or 'missing info' in out.lower(): return 'Rocket Raccoon'
    return 'Hulk'

def cap_router(state):
    out = state.node_outputs.get('Captain America', '')
    if 'VRAM_CEILING_HIT' in out:
        append_to_ledger('HALT: VRAM Ceiling Hit.')
        return 'END'
    return 'Black Widow'

def coulson_router(state):
    out = state.node_outputs.get('Agent Coulson', '').lower()
    if 'fail' in out:
        return 'Rocket Raccoon'
    return 'Quicksilver'

def spiderman_router(state):
    out = state.node_outputs.get('Spider-Man Env', '').lower()
    if 'fail' in out or 'bug' in out or 'error' in out:
        return 'Rocket Raccoon'
    return 'Heimdall'

def heimdall_router(state):
    out = state.node_outputs.get('Heimdall', '').lower()
    if 'fail' in out or 'bug' in out:
        return 'Rocket Raccoon'
    return 'Ultron'

hawkeye_route_node = Node.condition('Hawkeye Router', hawkeye_router)
cap_route_node = Node.condition('Cap Router', cap_router)
coulson_route_node = Node.condition('Coulson Router', coulson_router)
spiderman_route_node = Node.condition('Spider-Man Router', spiderman_router)
heimdall_route_node = Node.condition('Heimdall Router', heimdall_router)

workflow = Workflow('Hosteva_Swarm_v2_Full')

nodes = [nick_fury_node, vision_node, falcon_node, iron_man_arch_node, she_hulk_node, black_panther_node, wasp_ui_node, hawkeye_node, hulk_node, shang_chi_node, spider_man_plan_node, ant_man_node, jarvis_vram_node, captain_america_node, black_widow_node, iron_man_node, wasp_node, agent_coulson_node, jarvis_diag_node, quicksilver_node, spider_man_env_node, heimdall_node, ultron_node, thanos_node, star_lord_node, wanda_node, kang_node, shuri_node, rocket_raccoon_node, end_node, hawkeye_route_node, cap_route_node, coulson_route_node, spiderman_route_node, heimdall_route_node]

ids = {n.name(): workflow.add_node(n) for n in nodes}

workflow.connect(ids['Nick Fury'], ids['Vision'])
workflow.connect(ids['Vision'], ids['Falcon'])
workflow.connect(ids['Falcon'], ids['Iron Man Arch'])
workflow.connect(ids['Iron Man Arch'], ids['She-Hulk'])
workflow.connect(ids['She-Hulk'], ids['Black Panther'])
workflow.connect(ids['Black Panther'], ids['Wasp UI'])
workflow.connect(ids['Wasp UI'], ids['Hawkeye'])

workflow.connect(ids['Hawkeye'], ids['Hawkeye Router'])
workflow.connect(ids['Hawkeye Router'], ids['Rocket Raccoon'])
workflow.connect(ids['Hawkeye Router'], ids['Hulk'])

workflow.connect(ids['Hulk'], ids['Shang-Chi'])
workflow.connect(ids['Shang-Chi'], ids['Spider-Man Plan'])
workflow.connect(ids['Spider-Man Plan'], ids['Ant-Man'])
workflow.connect(ids['Ant-Man'], ids['Jarvis VRAM'])
workflow.connect(ids['Jarvis VRAM'], ids['Captain America'])

workflow.connect(ids['Captain America'], ids['Cap Router'])
workflow.connect(ids['Cap Router'], ids['END'])
workflow.connect(ids['Cap Router'], ids['Black Widow'])

workflow.connect(ids['Black Widow'], ids['Iron Man'])
workflow.connect(ids['Iron Man'], ids['Wasp'])
workflow.connect(ids['Wasp'], ids['Agent Coulson'])

workflow.connect(ids['Agent Coulson'], ids['Coulson Router'])
workflow.connect(ids['Coulson Router'], ids['Rocket Raccoon'])
workflow.connect(ids['Coulson Router'], ids['Quicksilver'])

workflow.connect(ids['Quicksilver'], ids['Spider-Man Env'])

workflow.connect(ids['Spider-Man Env'], ids['Spider-Man Router'])
workflow.connect(ids['Spider-Man Router'], ids['Rocket Raccoon'])
workflow.connect(ids['Spider-Man Router'], ids['Heimdall'])

workflow.connect(ids['Heimdall'], ids['Heimdall Router'])
workflow.connect(ids['Heimdall Router'], ids['Rocket Raccoon'])
workflow.connect(ids['Heimdall Router'], ids['Ultron'])

workflow.connect(ids['Ultron'], ids['Thanos'])
workflow.connect(ids['Thanos'], ids['Star-Lord'])
workflow.connect(ids['Star-Lord'], ids['Wanda'])
workflow.connect(ids['Wanda'], ids['Kang'])
workflow.connect(ids['Kang'], ids['Shuri'])
workflow.connect(ids['Shuri'], ids['END'])

def rocket_router(state):
    return 'END'
rocket_route_node = Node.condition('Rocket Router', rocket_router)
ids['Rocket Router'] = workflow.add_node(rocket_route_node)
workflow.connect(ids['Rocket Raccoon'], ids['Rocket Router'])
workflow.connect(ids['Rocket Router'], ids['END'])

if __name__ == '__main__':
    executor = Executor(local_config, timeout_seconds=3600)
    final_state = executor.execute(workflow)
    print('Workflow executed successfully.')
    outputs = final_state.get_all_node_outputs()
    print('Hawkeye:', outputs.get('Hawkeye'))
    print('Coulson:', outputs.get('Agent Coulson'))
