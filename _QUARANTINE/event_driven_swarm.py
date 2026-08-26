import os
from dotenv import load_dotenv
from graphbit import init, LlmConfig, Workflow, Executor, Node
from swarm_tools import run_shell_command, read_file, write_file

load_dotenv()
init()

def load_prompt(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f'ERROR: {filename} missing.'

# --- LLM Configs ---
# Using the local orchestrator model
local_config = LlmConfig.ollama('qwen-agent-32k:latest')

# Give tools to the agents
native_tools = [run_shell_command, read_file, write_file]

# --- Dynamic Backlog Injection ---
backlog_path = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPRINT_BACKLOG.md'
try:
    with open(backlog_path, 'r') as f:
        backlog_content = f.read()
except FileNotFoundError:
    backlog_content = "ERROR: SPRINT_BACKLOG.md not found."

# --- Nodes ---
# Nick Fury starts the sprint and evaluates the backlog
nick_fury_node = Node.agent(
    name='Nick Fury',
    prompt=f'Intake the following backlog:\n\n{backlog_content}',
    system_prompt=load_prompt('nick_fury_rules.md'),
    llm_config=local_config
)

# The Dev agents write the code
iron_man_node = Node.agent(
    name='Iron Man',
    prompt='Execute the backend tasks in the backlog. Use tools to write the code and run pytest.',
    system_prompt=load_prompt('iron_man_rules.md'),
    llm_config=local_config,
    tools=native_tools
)

# Agent Coulson is the Event Router. He reads the output of Iron Man's tools.
agent_coulson_node = Node.agent(
    name='Agent Coulson',
    prompt='Review the output of the previous agent. Did the tests pass? Use your tools to check the ledger or run pytest if needed.',
    system_prompt=load_prompt('agent_coulson_rules.md'),
    llm_config=local_config,
    tools=native_tools
)

# Rocket Raccoon is the Failsafe. He investigates hanging processes or critical failures.
rocket_raccoon_node = Node.agent(
    name='Rocket Raccoon',
    prompt='The tests failed or hung. Use your shell tool to run pytest, read the stack trace, and fix the code.',
    system_prompt=load_prompt('rocket_raccoon_rules.md'),
    llm_config=local_config,
    tools=native_tools
)

# --- Event-Driven Routers ---
# Instead of blind baton passes, Coulson mathematically evaluates the state.

def coulson_router(state):
    coulson_output = state.get('node_outputs', {}).get('Agent Coulson', '').lower()
    
    if 'timeout' in coulson_output or 'hung' in coulson_output or 'critical error' in coulson_output:
        print("\n[COULSON EVENT]: Process hung. Triggering Rocket Raccoon Failsafe.")
        return 'Rocket Raccoon'
    
    print("\n[COULSON EVENT]: Evaluation complete. Proceeding to End.")
    return 'END'

def rocket_router(state):
    rocket_output = state.get('node_outputs', {}).get('Rocket Raccoon', '').lower()
    if 'fail' in rocket_output or 'timeout' in rocket_output:
        print("\n[ROCKET EVENT]: Rocket failed to fix the issue. Escalating to human.")
        return 'END'
    print("\n[ROCKET EVENT]: Rocket fixed the issue. Returning to standard pipeline.")
    return 'END'

# Define the Router Nodes
coulson_route_node = Node.condition('Coulson Router', coulson_router)
rocket_route_node = Node.condition('Rocket Router', rocket_router)

# --- Build the Event-Driven Workflow ---
workflow = Workflow('Hosteva_Swarm_Event_Driven')

nodes = [
    nick_fury_node, 
    iron_man_node, 
    agent_coulson_node, 
    rocket_raccoon_node, 
    coulson_route_node, 
    rocket_route_node
]

end_node = Node.agent(name='END', prompt='Acknowledge completion.', system_prompt='You are the end node.', llm_config=local_config)
nodes.append(end_node)

ids = {n.name(): workflow.add_node(n) for n in nodes}

# Event Loop Connections
workflow.connect(ids['Nick Fury'], ids['Iron Man'])
workflow.connect(ids['Iron Man'], ids['Agent Coulson'])
workflow.connect(ids['Agent Coulson'], ids['Coulson Router'])

# Coulson routes to Rocket on failure, or END on success
workflow.connect(ids['Coulson Router'], ids['Rocket Raccoon'])
workflow.connect(ids['Coulson Router'], ids['END'])
workflow.connect(ids['Rocket Raccoon'], ids['Rocket Router'])

if __name__ == '__main__':
    # Use the native Executor with streaming to catch events in real-time
    workflow.set_graph_metadata('allow_cycles', True)
    executor = Executor(local_config, timeout_seconds=3600)
    
    print("\n🚀 IGNITING EVENT-DRIVEN SWARM...\n")
    
    # Listen to the live event stream
    for event in executor.execute_streaming(workflow, stream_mode="updates"):
        if event['event'] == 'node_started':
            print(f"[EVENT] Node Started: {event['node_name']}")
        elif event['event'] == 'tool_call_started':
            print(f"  -> 🛠️ Tool Execution: {event['tool_name']}")
        elif event['event'] == 'node_failed':
            print(f"[CRITICAL] Node Failed: {event['node_name']} - {event.get('error', 'Unknown Error')}")

    print('\n✅ Workflow execution completed.')
