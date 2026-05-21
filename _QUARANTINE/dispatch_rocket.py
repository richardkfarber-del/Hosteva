import os
from graphbit import init, LlmConfig, Workflow, Executor, Node

init()
local_config = LlmConfig.ollama('llama3.1-orchestrator')

def load_prompt(filename):
    try:
        with open(os.path.join('/home/rdogen/OpenClaw_Factory/projects/Hosteva/prompts', filename), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def read_file_safe(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return str(e)

ledger_content = read_file_safe('/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_loop.log')
dev_artifact = ""

dynamic_prompt = f"""
The Swarm has hit a 3-strike kickback limit. Analyze the following telemetry to determine the root cause.

=== RECENT SWARM LOGS ===
{ledger_content[-3000:]}

Identify the specific syntax error, missing permission, or hallucination. What is the proper fix?
"""

rocket_node = Node.agent(
    name='Rocket Raccoon', 
    prompt=dynamic_prompt, 
    system_prompt=load_prompt('rocket_rules.md'), 
    llm_config=local_config
)

workflow = Workflow('Rocket_Diag')
workflow.add_node(rocket_node)

executor = Executor(local_config, timeout_seconds=3600)
res = executor.execute(workflow)
print("ROCKET OUTPUT:")
print(res.get_all_node_outputs())
