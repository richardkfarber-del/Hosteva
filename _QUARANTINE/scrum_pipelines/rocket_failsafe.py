import sys
import json
from graphbit import init, LlmConfig, Workflow, Executor, Node

init()
local_config = LlmConfig.ollama('llama3.1-orchestrator')

def append_to_ledger(entry: str) -> str:
    with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md', 'a') as f:
        f.write(entry + '\n')
    return 'SUCCESS'

# Read state to get context and strikes
try:
    with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/swarm_state.json", "r") as f:
        state = json.load(f)
except:
    state = {"strikes": "unknown", "current_phase": "unknown"}

rocket_prompt = f"""
System Alert: The pipeline has hit the maximum strike limit.

State Data:
{json.dumps(state, indent=2)}

Your Task:
1. Identify which agent failed the task (e.g., Iron Man, Captain America).
2. Diagnose WHY they failed based on the kickback context or strike loop.
3. Recommend a specific fix to the pipeline or the code.
4. Log this failure to the ledger using your tool.
"""

rocket = Node.agent(name='Rocket Raccoon', prompt=rocket_prompt, system_prompt="You are Rocket Raccoon. You are a brilliant tactician and engineer. You diagnose systemic failures and fix them. Do not just insult the code; analyze the failure and provide a solution.", llm_config=local_config, tools=[append_to_ledger])

workflow = Workflow(name='Rocket_Failsafe')
workflow.add_node(rocket)

try:
    executor = Executor(local_config)
    print("Rocket Raccoon Failsafe Activated. Running diagnostics...")
    res = executor.execute(workflow)
    print("\n>>> [ROCKET RACCOON DIAGNOSTIC]:\n", res.get_node_output('Rocket Raccoon'))
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
